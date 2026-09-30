# [?] fix: ci-metrics deployment fixes (race condition, caching, nav)

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-02-13
Source: https://github.com/AztecProtocol/aztec-packages/commit/abb350663b04cfdbd23650f5e6f923079b0bb20d
Type: security-commit

## Details
fix: ci-metrics deployment fixes (race condition, caching, nav)

- Fix subprocess race condition with fcntl file lock
- Warm billing caches on startup with --preload
- Add test timings link to all dashboard nav bars
- Reduce gunicorn workers from 100 to 50
- Add METRICS_DB_PATH env var for SQLite location
- Fix Content-Encoding stripping for proxied responses
- Kill stale ci-metrics process before restart

## Patch
### ci3/ci-metrics/app.py
```diff
@@ -37,14 +37,26 @@ def verify_password(username, password):
 
 
 def _init():
-    """Initialize SQLite and start background threads."""
+    """Initialize SQLite, warm caches, and start background threads."""
     try:
         db.get_db()
         metrics.start_test_listener(r)
         metrics.start_ci_run_sync(r)
         print("[ci-metrics] Background threads started")
     except Exception as e:
         print(f"[ci-metrics] Warning: startup failed: {e}")
+    # Warm billing caches so first request isn't slow
+    try:
+        from billing.gcp import _ensure_cached as _warm_gcp
+        _warm_gcp()
+        print("[ci-metrics] GCP billing cache warmed")
+    except Exception as e:
+        print(f"[ci-metrics] GCP billing warmup failed: {e}")
+    try:
+        billing_aws.get_costs_overview()
+        print("[ci-metrics] AWS costs cache warmed")
+    except Exception as e:
+        print(f"[ci-metrics] AWS costs warmup failed: {e}")
 
 threading.Thread(target=_init, daemon=True, name='metrics-init').start()
 
```

### ci3/ci-metrics/billing/billing-dashboard.html
```diff
@@ -58,6 +58,7 @@
     <a href="/cost-overview">cost overview</a>
     <a href="/namespace-billing" class="active">namespace billing</a>
     <a href="/ci-insights">ci insights</a>
+    <a href="/test-timings">test timings</a>
   </div>
   <h2 style="margin:8px 0;color:#ccc;">namespace billing</h2>
 
```

### ci3/ci-metrics/db.py
```diff
@@ -7,7 +7,8 @@
 import sqlite3
 import threading
 
-_DB_PATH = os.path.join(os.getenv('LOGS_DISK_PATH', '/logs-disk'), 'metrics.db')
+_DB_PATH = os.getenv('METRICS_DB_PATH',
+                     os.path.join(os.getenv('LOGS_DISK_PATH', '/logs-disk'), 'metrics.db'))
 _local = threading.local()
 
 SCHEMA = """
```

### ci3/ci-metrics/views/ci-insights.html
```diff
@@ -62,6 +62,7 @@
     <a href="/cost-overview">cost overview</a>
     <a href="/namespace-billing">namespace billing</a>
     <a href="/ci-insights" class="active">ci insights</a>
+    <a href="/test-timings">test timings</a>
   </div>
 
   <h2 style="margin:8px 0;color:#ccc;">ci insights</h2>
```

### ci3/ci-metrics/views/cost-overview.html
```diff
@@ -74,6 +74,7 @@
     <a href="/cost-overview" class="active">cost overview</a>
     <a href="/namespace-billing">namespace billing</a>
     <a href="/ci-insights">ci insights</a>
+    <a href="/test-timings">test timings</a>
   </div>
 
   <h2 style="margin:8px 0;color:#ccc;">cost overview</h2>
```

### ci3/dashboard/Dockerfile
```diff
@@ -24,4 +24,4 @@ RUN pip install --no-cache-dir -r ci-metrics/requirements.txt
 RUN git config --global --add safe.directory /aztec-packages
 COPY . .
 EXPOSE 8080 8081
-CMD ["gunicorn", "-w", "100", "-b", "0.0.0.0:8080", "rk:app"]
+CMD ["gunicorn", "-w", "50", "-b", "0.0.0.0:8080", "rk:app"]
```

### ci3/dashboard/rk.py
```diff
@@ -27,30 +27,43 @@
 Compress(app)
 auth = HTTPBasicAuth()
 
-# Start the ci-metrics server as a subprocess
-# Check sibling dir (repo layout) then subdirectory (Docker layout)
+# Start the ci-metrics server as a subprocess (once across all workers).
+# Uses a file lock so only the first gunicorn worker to import this module
+# actually spawns the process; the rest skip silently.
+import fcntl
+import signal
+import time as _time
+
 _ci_metrics_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ci-metrics')
 if not os.path.isdir(_ci_metrics_dir):
     _ci_metrics_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ci-metrics')
 if os.path.isdir(_ci_metrics_dir):
-    # Kill any stale process on the port (e.g. leftover from previous reload)
-    import signal
+    _lock_path = f'/tmp/ci-metrics-{CI_METRICS_PORT}.lock'
     try:
-        out = subprocess.check_output(
-            ['lsof', '-ti', f':{CI_METRICS_PORT}'], stderr=subprocess.DEVNULL, text=True)
-        for pid in out.strip().split('\n'):
-            if pid:
-                os.kill(int(pid), signal.SIGTERM)
-        import time; time.sleep(0.5)
-    except (subprocess.CalledProcessError, OSError):
+        _lock_fd = open(_lock_path, 'w')
+        fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
+        # We hold the lock — kill stale process and spawn fresh one
+        try:
+            out = subprocess.check_output(
+                ['lsof', '-ti', f':{CI_METRICS_PORT}'], stderr=subprocess.DEVNULL, text=True)
+            for pid in out.strip().split('\n'):
+                if pid:
+                    os.kill(int(pid), signal.SIGTERM)
+            _time.sleep(0.5)
+        except (subprocess.CalledProcessError, OSError):
+            pass
+        _ci_metrics_env = {**os.environ, 'CI_METRICS_PORT': str(CI_METRICS_PORT)}
+        subprocess.Popen(
+            ['gunicorn', '-w', '4', '-b', f'0.0.0.0:{CI_METRICS_PORT}',
+             '--timeout', '120', '--preload', 'app:app'],
+            cwd=_ci_metrics_dir,
+            env=_ci_metrics_env,
+        )
+        print(f"[rk.py] ci-metrics server started on port {CI_METRICS_PORT}")
+        # Hold the lock until this process exits so other workers skip
+    except OSError:
+        # Another worker already holds the lock — nothing to do
         pass
-    _ci_metrics_env = {**os.environ, 'CI_METRICS_PORT': str(CI_METRICS_PORT)}
-    subprocess.Popen(
-        ['gunicorn', '-w', '4', '-b', f'0.0.0.0:{CI_METRICS_PORT}', '--timeout', '120', 'app:app'],
-        cwd=_ci_metrics_dir,
-        env=_ci_metrics_env,
-    )
-    print(f"[rk.py] ci-metrics server started on port {CI_METRICS_PORT}")
 
 def read_from_disk(key):
     """Read log from disk as fallback when Redis key not found."""
```

### ci3/merge_train_failure_slack_notify
```diff
@@ -31,8 +31,6 @@ elif [[ "$REF_NAME" == "merge-train/ci" ]]; then
   channel="#help-ci"
 elif [[ "$REF_NAME" == "merge-train/docs" ]]; then
   channel="#dev-rels"
-elif [[ "$REF_NAME" == "merge-train/fairies" ]]; then
-  channel="#team-fairies"
 elif [[ "$REF_NAME" == "merge-train/spartan" ]]; then
   channel="#team-alpha"
 else
```
