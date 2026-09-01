# [?] fix(mfs): fix fsync deadlock, set attrs, disable default caching (#11255)

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2026-04-02
Source: https://github.com/ipfs/kubo/commit/33e73a6cb64d8b618aed4220f15da3e5a0525183
Type: security-commit

## Details
fix(mfs): fix fsync deadlock, set attrs, disable default caching (#11255)

* fix(MFS): fix deadlock, attrs, caching

* unmount ipns and mfs in mount tests; allow offline

* set attrs Uid, Gid, and Valid for readonly and /ipns

* doc: update changelog

* fix(fuse): maximize kernel cache for immutable /ipfs paths

/ipfs content is addressed by CID and never changes, so kernel
attribute caching is safe and avoids unnecessary FUSE round-trips.
Also sets uid/gid on Root.Attr for consistency.

* docs: move FUSE changelog to v0.41 highlights

* fix(fuse): make IPNS fsync a no-op

Calling fsync on a file opened through /ipns deadlocks and eventually
panics, taking down the entire IPNS mount.

The Fsync handler called mfs.File.Flush(), which tries to open a
second write descriptor on the same file. Only one write descriptor
can exist at a time (desclock is exclusive), and the first one from
Open is still held. The new one blocks forever waiting for the lock.
After the FUSE timeout, Release tries to close the original descriptor
and hits a nil pointer panic in DagModifier.Sync.

Make Fsync a no-op, matching the MFS mount. Data gets flushed when
the file is closed. Also improve the MFS Fsync comment to explain
the same constraint.

* fix(fuse): set uid/gid on IPNS symlinks

The "local" symlink in /ipns showed uid=0 gid=0 (root) while
directories and files showed the daemon's uid/gid. Set uid/gid

_Trimmed to 38 lines — full report: https://github.com/ipfs/kubo/commit/33e73a6cb64d8b618aed4220f15da3e5a0525183_
