### Title
Webhook `shop-domain` Header Not Covered by HMAC Allows Shop-Identity Spoofing in Webhook Processing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` value that host applications use to attribute a webhook to a tenant is taken from an unsigned HTTP header. This breaks the equality "bytes verified == bytes acted upon," letting an attacker who can obtain any one valid `(raw_body, hmac)` pair (e.g., from a webhook legitimately delivered to their own installed shop) replay it to the app's public webhook endpoint with an arbitrary `shopify-shop-domain` header, causing the request to pass HMAC validation while being falsely attributed to a victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header without being part of the signed content: [1](#0-0) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which internally calls `request.to_signable_string` (i.e., only the body) and compares it against the `hmac` header: [2](#0-1) [3](#0-2) 

After HMAC succeeds, `request.shop` (the unauthenticated header value) is forwarded verbatim into `WebhookMetadata` and handed to the app's handler as the tenant identity for the event: [4](#0-3) 

This is the classic "bytes verified vs. bytes acted upon" identity-binding break called out in scope: the HMAC only binds the body, not the header that downstream code trusts as the shop identity. Because the body content for many webhook topics (especially the mandatory GDPR topics `shop/redact`, `customers/redact`, `customers/data_request`) is small, generic, or attacker-influenceable (an attacker can install the app on their own store and legitimately trigger these topics, or issue events with content they control, e.g. via test/uninstall/redact flows), an attacker can capture a `(raw_body, hmac)` pair that is valid under the app's real secret and then present it with the `shop-domain` header changed to a different, victim shop.

### Impact Explanation
Because `request.shop` is trusted by the handler as the authoritative tenant identifier without being covered by the signature, a forged/replayed webhook can cause the app to perform tenant-scoped actions (e.g., data redaction, customer data export/deletion for GDPR topics, or any custom handler logic keyed off `data.shop`) against a shop the attacker does not control. This is a cross-tenant identity confusion enabled purely by request replay/header substitution, meeting the "cross-tenant access" bar for Critical/High severity in this class of finding.

### Likelihood Explanation
The attacker needs only: (1) a legitimately app-installed shop they control (to receive at least one real, signed webhook delivery), and (2) the ability to POST directly to the app's public webhook endpoint with modified headers but the original body and HMAC. No access to `api_secret_key`, tokens, or any privileged credential is required — this is directly reachable by any unprivileged internet actor who is a legitimate (even free/trial) merchant of the target app.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the payload (e.g., via a canonicalized string that includes headers plus body) before computing/comparing the signature in `Request#to_signable_string` and `Utils::HmacValidator`. At minimum, document that host applications must independently corroborate `shop` with data retrieved via an authenticated GraphQL/REST call rather than trusting the header outright.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and captures a legitimately delivered webhook POST, including its raw body and its `X-Shopify-Hmac-Sha256` header (valid because it was signed by Shopify with the app's real secret).
2. Attacker crafts a new POST to the app's public webhook endpoint using the exact same raw body and `X-Shopify-Hmac-Sha256` value, but replaces `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into a request object; `Utils::HmacValidator.validate` succeeds because it only checks the (unchanged) raw body against the (unchanged) HMAC: [5](#0-4) 
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop` now resolves to `victim-shop.myshopify.com`, despite the HMAC never having certified that shop identity: [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
