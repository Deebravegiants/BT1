### Title
Webhook shop identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body [1](#0-0) . The `shop` value that is handed to the host application's handler (used to attribute the webhook payload to a tenant) comes from the unauthenticated `shopify-shop-domain` HTTP header, which is never part of the signed bytes [2](#0-1) . This breaks the equality "bytes verified" == "identity acted on": the HMAC verifies only `@raw_body`, while `request.shop` (and `topic`, `webhook_id`, `api_version`) are read straight from headers with no cryptographic binding to that body.

### Finding Description
`ShopifyAPI::Auth::Utils::HmacValidator.validate` computes and compares the HMAC exclusively over `verifiable_query.to_signable_string` [3](#0-2) . For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns just `@raw_body` [4](#0-3) , while `shop`, `topic`, `webhook_id`, and `api_version` are pulled from HTTP headers that are completely outside the signed payload [5](#0-4) .

`Registry.process` raises `InvalidWebhookError` only if the body HMAC fails; once it passes, it constructs `WebhookMetadata` directly from `request.shop`, `request.topic`, etc., and calls the registered handler [1](#0-0) . There is no secondary check binding the claimed `shop` to the body that was actually signed, and no verification that the shop belongs to a session/installation the app recognizes.

Equality that should hold but doesn't:
`HMAC-covered bytes (raw_body)` ⇏ `tenant identity acted upon (shop header)`

Because the same app-level `api_secret_key` is shared across every shop that installs the app, any merchant who legitimately installs the app on their own store receives real webhooks with valid HMACs for their own body content. That merchant can capture a `(raw_body, hmac)` pair from their own genuine webhook delivery and replay it to the app's webhook endpoint while substituting a different `shopify-shop-domain` header value belonging to another shop that also has the app installed. `Registry.process` will still accept it (the body's HMAC is unchanged and valid) and will hand the handler a `WebhookMetadata` claiming to be from the victim shop.

### Impact Explanation
If the host application trusts `WebhookMetadata#shop` to attribute/store data per tenant (the intended and only reasonable use of that field), a spoofed webhook lets one shop's operator inject fabricated data attributed to another shop — a cross-tenant data integrity/confusion issue. This matches the "Critical: cross-tenant access" impact category, since the tenant boundary (per-shop data ownership) is broken purely through this gem's own verification logic, without needing the app's `client_secret` or another shop's credentials — only the attacker's own legitimate valid webhook signature (which they possess for their own shop by design).

### Likelihood Explanation
Moderate. Exploitation requires an attacker who has installed the target app on their own shop (which is enough to legitimately receive signed webhooks), and a host application that (as documented/intended) dispatches on `WebhookMetadata#shop` without independently cross-checking it against the body or a known installed-shop list. No secret material, access token, or privileged account for the *victim* shop is required — only the attacker's own valid app installation.

### Recommendation
Bind the identifying fields (`shop`, `topic`) into the value that is HMAC-validated, or require callers of `Registry.process` to pass an expected shop/session and reject mismatches, rather than trusting unauthenticated headers for tenant attribution.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com` and receives a legitimate webhook: raw body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the shared `api_secret_key`), and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the exact same body `B` and HMAC `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `OpenSSL.secure_compare(computed_signature_of(B), H)` — this succeeds because `B` and `H` are unchanged [6](#0-5) .
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...)` [7](#0-6) , causing the host app to process attacker-controlled data as if it originated from `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
