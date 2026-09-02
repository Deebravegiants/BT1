This confirms the vulnerability path. The `shop-domain` header is read directly by `Registry.process` and handed to the app's handler as `data.shop`, but `HmacValidator.validate(request)` only signs `to_signable_string`, which returns `@raw_body` — the `shop-domain` header is never part of the signed payload.### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook replay/spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` binds `HmacValidator.validate` to `to_signable_string`, which only returns `@raw_body`. The `shop` (from the `shopify-shop-domain`/`x-shopify-shop-domain` header) is read separately via `shopify_header("shop-domain")` and is never included in the signed bytes. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC and then passes `request.shop` straight into the app's handler as the tenant identity (`WebhookMetadata.new(topic:, shop: request.shop, body:, ...)`), with no additional check that the shop is the one the signature actually covers.

### Finding Description
The identity binding that should hold is: `shop_bound_by_hmac == shop_acted_on`. In this gem it does not: `hmac == HMAC(secret, raw_body)` only, while `shop == header["shop-domain"]`, an unauthenticated field taken from the HTTP request and never mixed into the signed string [1](#0-0) .

`Registry.process` validates the HMAC purely against the body, then unconditionally forwards `request.shop` to the registered handler: [2](#0-1) .

Because every shop that installs the app shares the same `api_secret_key` (a single per-app secret, not per-shop), any tenant that has installed the app can legitimately obtain a validly-signed webhook payload (raw body + `X-Shopify-Hmac-Sha256`) for their own shop. That attacker-controlled tenant can then replay the exact same raw body and HMAC to the app's webhook endpoint while substituting the `shop-domain` header (or `x-shopify-shop-domain`) with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks `raw_body` against the secret [3](#0-2) , and `Registry.process` then hands the handler `shop: <victim-domain>` together with attacker-supplied `body` [2](#0-1) .

The documented usage pattern instructs app developers to trust `data.shop` as the tenant key when persisting/enqueuing webhook data (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), reinforcing that this gem's own documented contract treats `shop` as an authenticated field [4](#0-3) . The gem provides no mechanism, parameter, or warning indicating that `shop` is unauthenticated relative to the signature it validates.

### Impact Explanation
This breaks the tenant isolation the gem is supposed to provide for webhook processing: an attacker who is merely a legitimate installer of the app (no special privilege, no access to the app's `client_secret` or any other tenant's credentials) can cause the host application to process attacker-controlled webhook data under another shop's identity. Depending on how the host app's handler uses `data.shop` (e.g., selecting which shop record to update, which customer data-request/redact flow to run, or which order/customer webhook to apply), this enables cross-tenant data confusion or cross-tenant state corruption — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app with more than one installed tenant: the only prerequisite is that the attacker has installed the app on at least one shop (a completely unprivileged, self-service action), can capture their own valid webhook delivery (raw body + HMAC header, both visible to them as the receiving app or interceptable at their own endpoint), and can then send an HTTP POST to the app's public webhook route with a forged `shop-domain` header. No secret material, session, or token is required beyond what an ordinary/malicious merchant already legitimately possesses for their own install.

### Recommendation
Bind the shop domain (and ideally topic/webhook id) into the signed material, or otherwise cryptographically tie `shop` to the verified payload before trusting it as a tenant key. At minimum, `HmacValidator`/`Registry.process` should not allow the caller-supplied `shop-domain` header to be treated as authenticated data; the gem should document explicitly that `data.shop` is unauthenticated and instruct developers to cross-validate it against an independently known/authorized shop list, or Shopify should be asked to include the shop in the signed payload (matching how the OAuth `AuthQuery.to_signable_string` already includes `shop` in its signed string as a positive precedent) [5](#0-4) .

### Proof of Concept
1. Attacker installs the target app on shop `attacker.myshopify.com` (normal, unprivileged onboarding flow).
2. Shopify sends the attacker's app instance a legitimate webhook, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H = HMAC-SHA256(secret, B)` and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures `B` and `H` (they control their own endpoint / can log inbound requests).
4. Attacker crafts a new HTTP POST to the same app webhook endpoint with the identical raw body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses this into `hmac`, `shop = "victim.myshopify.com"`.
6. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and matches `H` — validation passes, since `shop` was never part of `to_signable_string`.
7. The registered handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and attacker-controlled `body`, and the host application processes it as an authentic event for the victim tenant.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
