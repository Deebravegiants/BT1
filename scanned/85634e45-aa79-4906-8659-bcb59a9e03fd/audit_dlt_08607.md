# [?] lpdeal: Fix adapter deadlock with duplicate pieces

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2024-03-14
Source: https://github.com/filecoin-project/lotus/commit/465ec58a7c7a705321b331ace7947731dd96ca07
Type: security-commit

## Details
lpdeal: Fix adapter deadlock with duplicate pieces

## Patch
### cmd/lotus-shed/lpdeal.go
```diff
@@ -3,6 +3,7 @@ package main
 import (
 	"bytes"
 	"context"
+	"database/sql"
 	"fmt"
 	"io"
 	"net"
@@ -452,6 +453,8 @@ var lpBoostProxyCmd = &cli.Command{
 
 			pieceUUID := uuid.New()
 
+			color.Blue("%s %s piece assign request with id %s", deal.DealProposal.PieceCID, deal.DealProposal.Provider, pieceUUID)
+
 			pieceInfoLk.Lock()
 			pieceInfos[pieceUUID] = append(pieceInfos[pieceUUID], pi)
 			pieceInfoLk.Unlock()
@@ -464,23 +467,36 @@ var lpBoostProxyCmd = &cli.Command{
 			// add piece entry
 
 			var refID int64
+			var pieceWasCreated bool
 
 			comm, err := db.BeginTransaction(ctx, func(tx *harmonydb.Tx) (commit bool, err error) {
-				// Add parked_piece, on conflict do nothing
 				var pieceID int64
-				err = tx.QueryRow(`
-					INSERT INTO parked_pieces (piece_cid, piece_padded_size, piece_raw_size)
-					VALUES ($1, $2, $3)
-					ON CONFLICT (piece_cid) DO UPDATE
-					SET piece_cid = EXCLUDED.piece_cid
-					RETURNING id`, deal.DealProposal.PieceCID.String(), int64(pieceSize.Padded()), int64(pieceSize)).Scan(&pieceID)
+				// Attempt to select the piece ID first
+				err = tx.QueryRow(`SELECT id FROM parked_pieces WHERE piece_cid = $1`, deal.DealProposal.PieceCID.String()).Scan(&pieceID)
+
 				if err != nil {
-					return false, xerrors.Errorf("upserting parked piece and getting id: %w", err)
+					if err == sql.ErrNoRows {
+						// Piece does not exist, attempt to insert
+						err = tx.QueryRow(`
+							INSERT INTO parked_pieces (piece_cid, piece_padded_size, piece_raw_size)
+							VALUES ($1, $2, $3)
+							ON CONFLICT (piece_cid) DO NOTHING
+							RETURNING id`, deal.DealProposal.PieceCID.String(), int64(pieceSize.Padded()), int64(pieceSize)).Scan(&pieceID)
+						if err != nil {
+							return false, xerrors.Errorf("inserting new parked piece and getting id: %w", err)
+						}
+						pieceWasCreated = true // New piece was created
+					} else {
+						// Some other error occurred during select
+						return false, xerrors.Errorf("checking existing parked piece: %w", err)
+					}
+				} else {
+					pieceWasCreated = false // Piece already exists, no new piece was created
 				}
 
 				// Add parked_piece_ref
 				err = tx.QueryRow(`INSERT INTO parked_piece_refs (piece_id, data_url)
-					VALUES ($1, $2) RETURNING ref_id`, pieceID, dataUrl.String()).Scan(&refID)
+        			VALUES ($1, $2) RETURNING ref_id`, pieceID, dataUrl.String()).Scan(&refID)
 				if err != nil {
 					return false, xerrors.Errorf("inserting parked piece ref: %w", err)
 				}
@@ -496,8 +512,28 @@ var lpBoostProxyCmd = &cli.Command{
 			}
 
 			// wait for piece to be parked
-
-			<-pi.done
+			if pieceWasCreated {
+				<-pi.done
+			} else {
+				// If the piece was not created, we need to close the done channel
+				close(pi.done)
+
+				go func() {
+					// close the data reader (drain to eof if it's not a closer)
+					if closer, ok := pieceData.(io.Closer); ok {
+						if err := closer.Close(); err != nil {
+							log.Warnw("closing pieceData in DataCid", "error", err)
+						}
+					} else {
+						log.Warnw("pieceData is not an io.Closer", "type", fmt.Sprintf("%T", pieceData))
+
+						_, err := io.Copy(io.Discard, pieceData)
+						if err != nil {
+							log.Warnw("draining pieceData in DataCid", "error", err)
+						}
+					}
+				}()
+			}
 
 			pieceIDUrl := url.URL{
 				Scheme: "pieceref",
```

### lib/harmony/harmonydb/sql/20240228-piece-park.sql
```diff
@@ -4,7 +4,7 @@ create table parked_pieces (
 
     piece_cid text not null,
     piece_padded_size bigint not null,
-    piece_raw_size text not null,
+    piece_raw_size bigint not null,
 
     complete boolean not null default false,
     task_id bigint default null,
```
