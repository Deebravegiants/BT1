### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC that `Registry.process` validates covers the JSON body alone. The `shop` value — read straight from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header — is never included in the signed content, yet it is forwarded unmodified into `WebhookMetadata#shop` and handed to the host application's `WebhookHandler#handle` as the tenant identifier for that event.

### Finding Description
The equality this gem is supposed to enforce is: `shop claimed in the request == shop cryptographically bound to the signed payload`. That equality is broken here.

- `Request#hmac` reads the signature header and `Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 
- `Request#shop` is a plain, unauthenticated header read with no cryptographic linkage to the signature: [2](#0-1) 
- `Registry.process` validates only `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (i.e., the raw body) against `verifiable_query.hmac`, and — on success — immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 
- `HmacValidator.validate`/`validate_signature` compute the HMAC purely over `verifiable_query.to_signable_string` (the body), never over the shop header: [4](#0-3) 
- The resulting `WebhookMetadata.shop` is a plain struct field with no independent verification, so whatever `Request#shop` returned is what the handler receives and acts on: [5](#0-4) 

Because Shopify apps share a single `client_secret`/`api_secret_key` across every shop that installs them, the HMAC secret is identical for all tenants of the app. An attacker who controls one installation of the app (their own shop) can:
1. Capture (or self-generate, by triggering a webhook on their own shop) a `(raw_body, valid HMAC)` pair that Shopify legitimately signed with the app's shared secret.
2. Replay that exact body and HMAC to the app's webhook endpoint, but substitute the `X-Shopify-Shop-Domain` header with a victim shop's domain.
3. `HmacValidator.validate` still succeeds because the signature only covers the body bytes, which are unmodified.
4. `Registry.process` calls `handler.handle` with `WebhookMetadata.shop` set to the attacker-chosen victim domain, even though the payload was never actually generated for that shop.

This is a direct structural analog to the `_withdraw` finding's root cause: state (here, tenant identity) is trusted/acted upon (`request.shop` forwarded to the handler) that was not protected by the same integrity mechanism (HMAC) that gates the rest of the operation, i.e. "bytes verified versus bytes parsed/trusted" and "shop authenticated versus shop stored/used as identity key."

### Impact Explanation
Any host application that uses this gem's webhook `Registry`/`Request` and relies on `WebhookMetadata#shop` to decide which tenant's data to update (a very common pattern — e.g. `shop/redact`, `app/uninstalled`, `orders/*` handlers keyed by `data.shop`) can be tricked into applying a webhook payload under the wrong shop's identity. This is a cross-tenant data-integrity/isolation issue: an attacker with a legitimate installation of the app can inject webhook events that the app's own logic will process as belonging to a different merchant, potentially triggering deletions, resyncs, unauthorized state changes, or misrouting of data to another tenant's account inside the host app's system — a cross-tenant access impact.

### Likelihood Explanation
Likelihood is Medium-High: the attacker only needs their own working installation of the target app (any developer/merchant can install a public Shopify app) to obtain a validly-signed `(body, hmac)` pair, since the same `api_secret_key` signs webhooks for every shop using that app. No access to Shopify's servers, the victim's shop, or the app's secret is required — only the ability to send an HTTP POST to the app's publicly reachable webhook endpoint with a modified header.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed material, or otherwise cryptographically verify that the `shop-domain` header matches the shop the payload was actually issued for, before trusting it:
```ruby
sig { override.returns(String) }
def to_signable_string
  # include the shop domain (and other identifying headers) in the signable content,
  # or independently verify shop against a value bound to the HMAC secret/session
  "#{shop}\n#{@raw_body}"
end
```
Since Shopify's own HMAC-SHA256 for webhooks is computed over the raw body only, the safer real-world fix is for `Registry.process` (or `Request`) to cross-check `request.shop` against an expected/registered shop for that specific webhook subscription (e.g., via the `webhook_id` looked up through the API) rather than trusting the header value verbatim, and to document to consumers that `WebhookMetadata#shop` is unauthenticated header data, not a value covered by HMAC verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker's shop legitimately triggers a webhook (e.g., updates a product), producing:
   - `raw_body = '{"id":123,...}'`
   - `X-Shopify-Hmac-Sha256 = <valid HMAC of raw_body under the app secret>`
   - `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
3. Attacker replays the exact same request to the app's webhook endpoint, only changing:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because the HMAC only covers `raw_body`: [3](#0-2) 
5. `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...))` is invoked, and the host app processes the event believing it is for `victim-shop.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
