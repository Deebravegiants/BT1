### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then forwards the `shop`, `topic`, `webhook_id`, and `api_version` values — all taken from unauthenticated HTTP headers — to the app's handler as trusted identity metadata. The `shop` value that identifies which tenant the webhook belongs to is never bound to the HMAC, breaking the equality `hmac_verified_bytes == identity_bytes_acted_on`.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook using: [1](#0-0) 

The HMAC check is performed by `Utils::HmacValidator.validate`, which in turn calls `to_signable_string` on the request object: [2](#0-1) 

For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only the raw body — none of the HTTP headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) are part of the signed material: [3](#0-2) 

Yet `Registry.process` extracts `request.shop` (parsed straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header) and passes it, unchecked, to the app's webhook handler as the authoritative tenant identity for that event: [4](#0-3) 

Because only the body bytes are authenticated, any party who has previously received one legitimate (body, HMAC) pair from Shopify for the app (e.g., a malicious merchant who has installed the app on their own shop, or any user in possession of a previously delivered/leaked payload) can replay that exact body+HMAC to the app's public webhook endpoint while substituting the `shopify-shop-domain` header with an arbitrary victim shop domain. `HmacValidator.validate` will still succeed (body and signature are unmodified), and the handler will receive `WebhookMetadata` claiming the event originated from the attacker-chosen shop: [5](#0-4) 

The break in identity binding is:
`hmac_valid(body, secret) == true` should imply `shop == the tenant that actually generated body`, but the gem only proves `hmac_valid(body, secret) == true`; `shop` is an independent, attacker-controlled input.

### Impact Explanation
This allows cross-tenant data injection/spoofing in any multi-tenant app built on this gem: an attacker who is a legitimate (if malicious) merchant of the app — or anyone who obtains one valid webhook body/HMAC pair for the app's `client_secret` — can cause the app to process fabricated events "on behalf of" a different, victim shop. Depending on what the host app's webhook handler does with `data.shop` (e.g., updating per-shop state, triggering redactions such as `shop/redact`/`customers/redact`, writing to the victim's records), this can corrupt another tenant's data or trigger unintended actions attributed to them — a cross-tenant access impact.

### Likelihood Explanation
Exploitation requires the attacker to have obtained at least one genuine `(raw_body, hmac)` pair produced with the app's `client_secret`. In a multi-tenant SaaS app, this is trivially available to any attacker who installs the app on their own (attacker-controlled) shop — they will legitimately receive real webhooks with valid HMACs for their own shop and can then simply resend that exact payload to the app's public webhook endpoint with a different `shop-domain` header. No knowledge of `client_secret` itself is required, only possession of one previously delivered payload, which makes this readily reachable for any user who can sign up as a merchant of the target app.

### Recommendation
Bind the shop identity to the authenticated payload rather than trusting the header value in isolation:
- Include the `shop-domain` (and ideally `topic`/`webhook_id`) header values in the HMAC-signed material (e.g., concatenate them with the body before computing/verifying the signature), or
- Require host applications to cross-verify `request.shop` against the shop reference embedded within the verified body/session context before trusting it, and document this requirement prominently in `docs/usage/webhooks.md`.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, a shop they control.
2. Shopify delivers a legitimate webhook to the app's endpoint with headers:
   `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of body B>`, body `B`.
3. Attacker captures `(B, valid_hmac)` and replays it directly to the same public webhook endpoint, changing only the header:
   `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` are unaffected by the header change (only `@raw_body` is signed), so `Utils::HmacValidator.validate` returns `true`.
5. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)`, and the app processes attacker-supplied data as if it belongs to `victim-shop.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
