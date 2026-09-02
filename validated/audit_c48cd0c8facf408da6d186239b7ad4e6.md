### Title
Webhook `shop` identity not bound by HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates the webhook's HMAC by calling `Utils::HmacValidator.validate(request)`, but the `Request#to_signable_string` used for that signature only covers the raw body, never the `shop` value. `WebhookMetadata` (and thus the app's handler) is then built using `request.shop`, which is read straight from the unauthenticated `X-Shopify-Shop-Domain` / `shopify-shop-domain` header. This breaks the identity binding: `hmac(raw_body)` is verified, while `shop` (the tenant identifier the app relies on) travels outside that signature.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` with: [1](#0-0) 
- `hmac` is read from the `hmac-sha256` header.
- `shop` is read from the `shop-domain` header.
- `to_signable_string` returns only `@raw_body`. [2](#0-1) 

`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to `verifiable_query.hmac`: [3](#0-2) 

Since `to_signable_string` is only the raw body, the signature that Shopify computes and sends (`X-Shopify-Hmac-Sha256`) is `HMAC(client_secret, raw_body)` — it never incorporates the shop domain. `Registry.process` uses this same validation and then unconditionally trusts `request.shop` to build `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because a single app uses **one shared `client_secret`** across every shop that installs it, any shop where the app is installed can capture a legitimate webhook delivery it receives (raw body + valid HMAC, both signed with the same secret used for all tenants) and replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a different, victim shop. The HMAC check in `HmacValidator.validate` still passes (it only checks the body), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop: [5](#0-4) 

This is the equality violated: `hmac_verified_bytes == raw_body` while `identity_used_by_handler == shop_header`, i.e., `shop` is a field acted on by the app but not covered by the HMAC.

Downstream host apps are documented to use `data.shop` returned by the handler to select the tenant session/record to act on (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`): [6](#0-5) 

### Impact Explanation
An attacker who controls one shop installation of a multi-tenant app can forge webhook deliveries that the receiving app believes originate from any other shop using the same app (cross-tenant confusion). Depending on how the host app uses `data.shop` (e.g., to look up and mutate the victim's stored session/data, or to trigger shop-scoped business logic), this can lead to cross-tenant data corruption or unauthorized actions performed against another merchant's data — meeting the "cross-tenant access" bar for High/Critical impact, since the trust boundary between tenants sharing the same `client_secret` is broken.

### Likelihood Explanation
Likelihood is high in any scenario where the attacker is a legitimate (even free/trial) installer of the target app — a bar that is trivial to clear for public apps. No access to `api_secret_key` or any privileged credential is required; the attacker only needs to intercept traffic to their own webhook endpoint (which they control) and replay it with a modified header to the app's public webhook route.

### Recommendation
Bind the identity fields used by the handler into the HMAC-verified payload, or otherwise independently authenticate `shop`:
- Include `shop` (and ideally `topic`, `webhook_id`) in the signable string/verification step, or
- Cross-check `request.shop` against the shop associated with the session/subscription that was registered for the specific `webhook_id`/topic before dispatching to the handler, rather than trusting the header verbatim.
- At minimum, document prominently that `data.shop` in `WebhookMetadata` is not itself HMAC-protected and must not be used as an authoritative tenant identifier without additional server-side verification (e.g., matching against webhook IDs registered per shop).

### Proof of Concept
1. App `client_secret` is shared across all shops that install App X.
2. Attacker installs App X on `attacker.myshopify.com` and registers for topic `orders/create`.
3. Shopify delivers a webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: HMAC(secret, B)`, `X-Shopify-Shop-Domain: attacker.myshopify.com`.
4. Attacker captures this raw request (they own the endpoint they registered, or use a proxy/relay), then re-sends the identical `raw_body` and `hmac-sha256` header to the same app endpoint, replacing only `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, raw_body)` — this still matches because `to_signable_string` never included `shop`. Validation passes.
6. `WebhookMetadata.new(... shop: request.shop ...)` is built with `shop: "victim.myshopify.com"` and passed to the app's handler, which now processes attacker-controlled data as if it came from `victim.myshopify.com`.

Note: I was unable to inspect `lib/shopify_api/webhooks/webhook_metadata.rb` and how every downstream `WebhookHandler` implementation in the wild consumes `data.shop`, since that logic lives in host applications outside this gem's indexed scope; the concrete blast radius (data corruption vs. more limited effects) depends on that host-side usage, which could not be further verified here.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
