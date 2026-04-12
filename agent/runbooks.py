RUNBOOKS = {
    "database": {
        "name": "Database Incident Runbook",
        "steps": [
            "1. Check DB connection count: SELECT count(*) FROM pg_stat_activity;",
            "2. Check for long-running queries: SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE state = 'active';",
            "3. Kill blocking queries if needed: SELECT pg_terminate_backend(pid);",
            "4. Check max_connections in postgresql.conf",
            "5. Restart connection pooler (PgBouncer) if configured",
            "6. Escalate to DBA if issue persists"
        ]
    },
    "kubernetes": {
        "name": "Kubernetes Incident Runbook",
        "steps": [
            "1. Check pod status: kubectl get pods -A",
            "2. Describe failing pod: kubectl describe pod <pod-name>",
            "3. Check pod logs: kubectl logs <pod-name> --previous",
            "4. Check config maps: kubectl get configmap -o yaml",
            "5. Check secrets are mounted: kubectl get secrets",
            "6. Force rollout restart: kubectl rollout restart deployment/<name>"
        ]
    },
    "memory": {
        "name": "Memory / OOM Runbook",
        "steps": [
            "1. Check memory usage: free -h or top",
            "2. Find memory-hungry processes: ps aux --sort=-%mem | head -10",
            "3. Check for memory leaks in app logs",
            "4. Restart affected service if safe to do so",
            "5. Increase pod memory limits in k8s if needed",
            "6. Profile the application for leak root cause"
        ]
    },
    "cpu": {
        "name": "High CPU Runbook",
        "steps": [
            "1. Identify top CPU processes: top or htop",
            "2. Check for runaway jobs or infinite loops in logs",
            "3. Kill rogue process if identified: kill -9 <pid>",
            "4. Check recent deployments that may have introduced the issue",
            "5. Scale horizontally if load is legitimate",
            "6. Add CPU alerts for early detection"
        ]
    },
    "ssl": {
        "name": "SSL Certificate Runbook",
        "steps": [
            "1. Check cert expiry: openssl s_client -connect domain.com:443 | openssl x509 -noout -dates",
            "2. Renew with certbot: certbot renew --force-renewal",
            "3. Reload nginx: systemctl reload nginx",
            "4. Verify cert is valid: curl -I https://domain.com",
            "5. Fix auto-renewal cron if broken",
            "6. Set up expiry monitoring alert (30 days before)"
        ]
    },
    "disk": {
        "name": "Disk Space Runbook",
        "steps": [
            "1. Check disk usage: df -h",
            "2. Find large files: du -sh /* | sort -rh | head -20",
            "3. Clear old logs: journalctl --vacuum-time=7d",
            "4. Check and apply log rotation: logrotate -f /etc/logrotate.conf",
            "5. Remove unused Docker images: docker system prune -a",
            "6. Set up disk usage alerts at 80% threshold"
        ]
    },
    "network": {
        "name": "Network / API Runbook",
        "steps": [
            "1. Check service health: curl -I http://service-url/health",
            "2. Test DNS resolution: nslookup domain.com",
            "3. Check firewall rules: iptables -L or security groups",
            "4. Verify load balancer health checks",
            "5. Check rate limiting configs",
            "6. Review recent network policy changes"
        ]
    },
    "general": {
        "name": "General Incident Runbook",
        "steps": [
            "1. Identify affected services and scope",
            "2. Check recent deployments in last 24 hours",
            "3. Review error logs for spike patterns",
            "4. Check monitoring dashboards (Grafana/Datadog)",
            "5. Communicate status to stakeholders",
            "6. Document findings in incident report"
        ]
    }
}

def get_runbook(incident_type: str) -> dict:
    """Get the most relevant runbook for an incident type."""
    incident_lower = incident_type.lower()
    for key in RUNBOOKS:
        if key in incident_lower:
            return RUNBOOKS[key]
    return RUNBOOKS["general"]

def get_all_runbook_names() -> list:
    return [f"{k}: {v['name']}" for k, v in RUNBOOKS.items()]