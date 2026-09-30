# [?] [event] fix underflow read in event_ring_util.c

## Summary
Severity: Unknown
Chain: Monad
Component: monad-crypto/monad
Published: 2025-09-05
Source: https://github.com/category-labs/monad/commit/b821362c3441fdf063bd216634d46d3dd2bc8b15
Type: security-commit

## Details
[event] fix underflow read in event_ring_util.c

If the buffer can't hold the full size of the file or a short read
occurs, it won't be null-terminated, and strsep will have undefined
behavior. Because of how procfs(5) works we don't expect this to
happen, but the comment (showing the format explicitly) also documents
the code better.

## Patch
### category/core/event/event_ring_util.c
```diff
@@ -105,16 +105,26 @@ static int find_existing_parent_path(char const *path, char **parent_path)
 
 static bool is_writer_fd(ino_t ring_ino, int fdinfo_entry)
 {
-    char const FDINFO_DELIM[] = "\t :";
-    char read_buf[256];
+    // The format of an fdinfo file (as of Linux 6.16, see proc/fd.c) is:
+    //
+    //   "pos:\t%lli\nflags:\t0%o\nmnt_id:\t%i\nino:\t%lu\n"
+    //
+    // This will definitely fit in READ_BUF_SIZE bytes, if not the format
+    // must have changed somehow and we won't try to parse it.
+    constexpr char FDINFO_DELIM[] = "\t :";
+    constexpr size_t READ_BUF_SIZE = 256;
+    char read_buf[READ_BUF_SIZE];
     char *scan = read_buf;
     char *line;
-    if (read(fdinfo_entry, read_buf, sizeof read_buf) == -1) {
+
+    ssize_t const n_read = read(fdinfo_entry, read_buf, sizeof read_buf);
+    if (n_read == -1 || n_read == READ_BUF_SIZE) {
         return false;
     }
     bool is_write = false;
     bool is_ino = false;
 
+    read_buf[n_read] = '\0'; // In case of a short read
     while ((line = strsep(&scan, "\n"))) {
         char *key, *value = nullptr;
         key = strsep(&line, FDINFO_DELIM);
```
