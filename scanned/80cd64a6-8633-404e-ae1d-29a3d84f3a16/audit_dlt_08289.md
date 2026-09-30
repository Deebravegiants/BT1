# [?] fdctl: fix crash if config file doesn't exist

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-05-08
Source: https://github.com/firedancer-io/firedancer/commit/5e8e66a782e1a75106c6f24dd5f38f90bd145bf1
Type: security-commit

## Details
fdctl: fix crash if config file doesn't exist

## Patch
### src/app/shared/boot/fd_boot.c
```diff
@@ -107,7 +107,7 @@ fd_main_init( int *        pargc,
     ulong user_config_sz = 0UL;
     if( FD_LIKELY( user_config_path ) ) {
       user_config = fd_file_util_read_all( user_config_path, &user_config_sz );
-      if( FD_UNLIKELY( !user_config ) ) FD_LOG_ERR(( "failed to read user config file `%s` (%d-%s)", user_config_path, errno, fd_io_strerror( errno ) ));
+      if( FD_UNLIKELY( user_config==MAP_FAILED ) ) FD_LOG_ERR(( "failed to read user config file `%s` (%d-%s)", user_config_path, errno, fd_io_strerror( errno ) ));
     }
 
     int netns = fd_env_strip_cmdline_contains( pargc, pargv, "--netns" );
```

### src/app/shared/fd_file_util.h
```diff
@@ -77,10 +77,10 @@ int
 fd_file_util_self_exe( char path[ PATH_MAX ] );
 
 /* fd_file_util_read_all() reads all the file contents from the provided
-   path into a newly `mmap(2)`ed region.  Returns MAP_FAILURE on failure
-   and errno will be set appropriately.  The caller is responsible for
-   unmapping the memory when they are done.  On success, out_sz will be
-   set to the file size.  Otherwise, the value of out_sz is undefined. */
+   path into a newly `mmap(2)`ed region.  Returns MAP_FAILED on failure.
+   The caller is responsible for unmapping the region when done.
+   On success, out_sz will be set to the file size.  Otherwise, the
+   value of out_sz is undefined. */
 
 char *
 fd_file_util_read_all( char const * path,
```
