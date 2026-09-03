# [H] Arbitrary File Download as Shopmanager

## Summary
Severity: High
Program: Automattic
Weakness: Path Traversal
Reporter: simonscannell
State: resolved
Disclosed: 2019-12-19T14:23:57.394Z
Source: https://hackerone.com/reports/402473

## Details
Due to a flaw in the way WooCommerce handles downloadable products, a shop manager can download arbitrary files on the server.

The video shows the exploit and how simple it is:
https://www.youtube.com/watch?v=bkrHpqht5SM

The function responsible for validating the download file input is the following:
(/woocommerce/includes/abstracts/abstract-wc-product.php)
```
	public function set_downloads( $downloads_array ) {
		$downloads = array();
		$errors    = array();

		foreach ( $downloads_array as $download ) {
			if ( is_a( $download, 'WC_Product_Download' ) ) {
				$download_object = $download;
			} else {
				$download_object = new WC_Product_Download();

				// If we don't have a previous hash, generate UUID for download.
				if ( empty( $download['download_id'] ) ) {
					$download['download_id'] = wp_generate_uuid4();
				}

				$download_object->set_id( $download['download_id'] );
				$download_object->set_name( $download['name'] );
				$download_object->set_file( $download['file'] );
			}

			// Validate the file extension.
			if ( ! $download_object->is_allowed_filetype() ) {
				if ( $this->get_object_read() ) {
					/* translators: %1$s: Downloadable file */
					$errors[] = sprintf( __( 'The downloadable file %1$s cannot be used as it does not have an allowed file type. Allowed types include: %2$s', 'woocommerce' ), '<code>' . basename( $download_object->get_file() ) . '</code>', '<code>' . implode( ', ', array_keys( $download_object->get_allowed_mime_types() ) ) . '</code>' );
				}
				continue;
			}

			// Validate the file exists.
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/402473_
