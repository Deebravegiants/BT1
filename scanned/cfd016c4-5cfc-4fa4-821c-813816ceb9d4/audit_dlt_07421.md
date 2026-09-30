# [?] fix: remove gunicorn --preload to prevent ci-metrics deadlock

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-02-13
Source: https://github.com/AztecProtocol/aztec-packages/commit/12700d68cb2e616d6a2d4d8a9cc56f7aa5996cc9
Type: security-commit

## Details
fix: remove gunicorn --preload to prevent ci-metrics deadlock

gunicorn 25.x introduced a control socket that deadlocks when combined
with --preload. The worker process gets stuck after fork and never
serves requests. Removing --preload fixes the issue.

## Patch
### ci3/dashboard/rk.py
```diff
@@ -55,7 +55,7 @@
         _ci_metrics_env = {**os.environ, 'CI_METRICS_PORT': str(CI_METRICS_PORT)}
         subprocess.Popen(
             ['gunicorn', '-w', '1', '-b', f'0.0.0.0:{CI_METRICS_PORT}',
-             '--timeout', '120', '--preload', 'app:app'],
+             '--timeout', '120', 'app:app'],
             cwd=_ci_metrics_dir,
             env=_ci_metrics_env,
         )
```
