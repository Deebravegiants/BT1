# [M] Note Mark: Unauthenticated disclosure of soft-deleted note metadata via deleted=true on public books

## Summary
Severity: Medium
Advisory: GHSA-588f-fvcv-xhvf
CVE: CVE-2026-50554
CWE: CWE-200, CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-588f-fvcv-xhvf
Type: github-advisory

## Affected
- Go: `github.com/enchant97/note-mark/backend` — affected >=0 <0.0.0-20260601210758-9c9b72740f22

## Details
Summary

  GET /api/books/{bookID}/notes is an unauthenticated endpoint that accepts a "deleted" query parameter. When the request is ?deleted=true, the
  service runs the query with Unscoped() (bypassing GORM's soft-delete scope) but keeps the read-authorization clause as "owner_id = ? OR is_public
  = ?". As a result, any unauthenticated caller can enumerate the metadata of soft-deleted ("trashed") notes belonging to any public book — notes
  the owner explicitly deleted and expected to be removed from public view.

  Affected component (code-verified)

  backend/services/notes.go — GetNotesByBookID (lines 72-89):

  func (s NotesService) GetNotesByBookID(currentUserID *uuid.UUID, bookID uuid.UUID, deleted bool) ([]db.Note, error) {
        tx := db.DB
        if deleted {
                tx = tx.Unscoped() // <-- bypasses soft-delete scope
        }
        tx = tx.
                Preload("Book").
                Joins("JOIN books ON books.id = notes.book_id").
                Where(
                        db.DB.Where("books.id = ?", bookID),
                        db.DB.Where("owner_id = ? OR is_public = ?", currentUserID, true), // <-- is_public still honored for trash
                )
        if deleted {
                tx = tx.Where("notes.deleted_at IS NOT NULL")
        }
        var notes []db.Note
        return notes, dbErrorToServiceError(tx.Find(&notes).Error)
  }

  Route registration confirms the endpoint has no AuthRequiredMiddleware (backend/handlers/notes.go:37), and the deleted flag is attacker-controlled
   (backend/handlers/notes.go:86 — Deleted bool with query:"deleted").

  Proof of concept

  1. A victim owns a public book (is_public = true), creates a note, then soft-deletes it (moves it to trash). The note still exists in the DB with
  deleted_at set.
  2. An unauthenticated attacker who knows (or enumerates) the book UUID requests: GET /api/books/<bookID>/notes?deleted=true
  3. The response lists the soft-deleted note(s) — id, title, slug, timestamps — even though the attacker is not authenticated and the owner
  intended the note to be deleted.

  Impact

  Exposure of soft-deleted note metadata (title, slug, timestamps) of public books to unauthenticated actors. The note body is not exposed — the
  content endpoint (GetNoteContent) does not use Unscoped(), so its count query returns 0 for soft-deleted notes and yields 404. Impact is therefore
   limited to metadata disclosure and the bypass of the intended "delete" semantics on public books.

  Remediation

  Restrict trash (soft-deleted) listings to the book owner only — never honor the is_public branch when deleted=true:

   func (s NotesService) GetNotesByBookID(currentUserID *uuid.UUID, bookID uuid.UUID, deleted bool) ([]db.Note, error) {
        tx := db.DB
        if deleted {
                tx = tx.Unscoped()
        }
  +     // Soft-deleted ("trash") notes must only ever be listed to the book owner.
  +     authz := db.DB.Where("owner_id = ? OR is_public = ?", currentUserID, true)
  +     if deleted {
  +             authz = db.DB.Where("owner_id = ?", currentUserID)
  +     }
        tx = tx.
                Preload("Book").
                Joins("JOIN books ON books.id = notes.book_id").
                Where(
                        db.DB.Where("books.id = ?", bookID),
  -                     db.DB.Where("owner_id = ? OR is_public = ?", currentUserID, true),
  +                     authz,
                )
        if deleted {
                tx = tx.Where("notes.deleted_at IS NOT NULL")
        }
        var notes []db.Note
        return notes, dbErrorToServiceError(tx.Find(&notes).Error)
   }

  With this change, when currentUserID is nil (unauthenticated) and deleted=true, the clause becomes owner_id = NULL, which matches nothing — so
  trash is never exposed to anonymous callers.

  Coordinated disclosure / CVE request

  We have reported this privately and are happy to assist with any further validation or testing you need. If you agree this qualifies as a security
   vulnerability, we would be grateful if you could request a CVE ID for it — GitHub lets maintainers request a CVE directly from this advisory page
   once it is accepted. Thank you for your time and for maintaining note-mark.

  References

  - CWE-200: Exposure of Sensitive Information to an Unauthorized Actor
  - CWE-285: Improper Authorization
  - Prior note-mark authorization fix (CVE-2026-40265) established that read paths must scope by owner_id OR is_public; this report covers the trash
   path that the scope did not fully cover.

  ---

## References
- https://github.com/enchant97/note-mark/security/advisories/GHSA-588f-fvcv-xhvf
- https://github.com/enchant97/note-mark/commit/9c9b72740f22a06131a8f64b53bb08e3b05b81a6
- https://github.com/enchant97/note-mark
