# [?] gossmap: fix OpenBSD crash.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2024-02-27
Source: https://github.com/ElementsProject/lightning/commit/87f6ceb72111e09fa422c6b0a908c7f1092438dc
Type: security-commit

## Details
gossmap: fix OpenBSD crash.

Thanks to amazing debugging assistance from grubles, we figured out
that indeed, my memory was correct: write and mmap are not consistent
on all platforms.  The easiest fix is to disable mmap on OpenBSD for now:
the better fix is to do in-place updates using the mmap, and only rely
on write() for append (which always causes a remap anyway before it's accessed).

Fixes: https://github.com/ElementsProject/lightning/issues/7109
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### common/gossmap.c
```diff
@@ -690,9 +690,13 @@ static bool load_gossip_store(struct gossmap *map)
 {
 	map->map_size = lseek(map->fd, 0, SEEK_END);
 	map->local = NULL;
+
+	/* gossipd uses pwritev(), which is not consistent with mmap on OpenBSD! */
+#ifndef __OpenBSD__
 	/* If this fails, we fall back to read */
 	map->mmap = mmap(NULL, map->map_size, PROT_READ, MAP_SHARED, map->fd, 0);
 	if (map->mmap == MAP_FAILED)
+#endif /* __OpenBSD__ */
 		map->mmap = NULL;
 
 	/* We only support major version 0 */
@@ -994,8 +998,11 @@ bool gossmap_refresh_mayfail(struct gossmap *map, bool *updated)
 	if (map->mmap)
 		munmap(map->mmap, map->map_size);
 	map->map_size = len;
+	/* gossipd uses pwritev(), which is not consistent with mmap on OpenBSD! */
+#ifndef __OpenBSD__
 	map->mmap = mmap(NULL, map->map_size, PROT_READ, MAP_SHARED, map->fd, 0);
 	if (map->mmap == MAP_FAILED)
+#endif /* __OpenBSD__ */
 		map->mmap = NULL;
 
 	return map_catchup(map, updated);
```
