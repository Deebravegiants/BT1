I have enough evidence to write the finding.### Title
Webhook `shop-domain` header is trusted for tenant attribution without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw HTTP body only, but the `shop` (tenant identity) that gets propagated to the app's `WebhookHandler` is read from the `X-Shopify-Shop-Domain` HTTP header, which is never included in the signed content. This breaks the identity binding `hmac-signed bytes == data acted upon`, analogous to the FrankenDAO bug where a value (`proposalsCreated`/`proposalsPassed`) was acted upon without being covered by the check that was supposed to gate it (`veto` didn't touch counters it should have bound to the "malicious" determination).

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`: [1](#0-0) 
- `hmac` is read from the `hmac-sha256` header.
- `shop` is read from the `shop-domain` header.
- `to_signable_string` returns only `@raw_body`: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC strictly over `to_signable_string`, i.e., only the raw body bytes: [3](#0-2) 

`Registry.process` accepts the request once the body-only HMAC check passes, then forwards `request.shop` (the unauthenticated header value) straight into `WebhookMetadata`, which is handed to the app's handler as the trusted tenant identifier: [4](#0-3) [5](#0-4) 

The gem's own documentation instructs host apps to trust `data.shop` for tenant-scoped work (e.g., enqueuing a job keyed by `shop_domain: data.shop`): [6](#0-5) 

This differs from the OAuth callback path, where `AuthQuery#to_signable_string` explicitly includes `shop` as part of the signed content, so `shop` there is cryptographically bound to the signature: [7](#0-6) 

For webhooks, no equivalent binding exists: the equality the gem should enforce — `shop header used for tenant routing == shop bound inside the HMAC-signed payload` — does not hold, because the signed bytes (`raw_body`) say nothing about `shop`.

### Impact Explanation
Any party capable of obtaining one genuine, HMAC-valid webhook body+signature pair for the app (e.g., an attacker who installs the app on their own store, which is normal unprivileged access to a Shopify Partner/dev account) can capture that `(raw_body, hmac)` pair and replay it to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header value naming a victim shop. Because `HmacValidator.validate` only checks the body against the signature, the check still passes; `Registry.process` then invokes the handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop domain. Any host application that uses `data.shop` to key tenant-scoped side effects (persisting redact/data-request records, updating per-shop caches, dispatching per-shop background jobs, as shown in the gem's own example) will attribute attacker-controlled data to a victim tenant — a cross-tenant data-integrity/confusion issue reachable by an unprivileged internet user who only needs their own valid installation, satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is moderate: it requires the attacker to have (or obtain) a legitimately signed webhook body from their own store (trivial — install the app, trigger a webhook, capture body+HMAC via a proxy) and to control HTTP headers when POSTing to the target endpoint (straightforward, since attacker is an ordinary internet client sending an HTTP request to the same publicly reachable callback path). No access to `api_secret_key`, tokens, or the merchant's account is required.

### Recommendation
Bind the `shop` (and ideally `topic`/`api_version`/`webhook_id`) to the HMAC verification, not just the raw body: either include these header values in the signed content by composing an application-level canonical string checked separately, or, more robustly, resolve the tenant strictly from a value that Shopify itself binds to the signature/body (Shopify does not currently sign headers for webhooks, so a stronger mitigation is for the host app / this gem to require a strict shop-domain to registered-webhook mapping lookup, or track `webhook_id` uniqueness plus enforce that `shop` matches an app's currently registered shop for that topic before trusting it) rather than passing the raw header value straight through to `WebhookMetadata` as an implicitly trusted field.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and captures a legitimate webhook delivery, e.g. `orders/create`, obtaining `raw_body` and the valid `X-Shopify-Hmac-Sha256` header (computed with the app's real `client_secret` by Shopify).
2. Attacker replays the exact same `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request#hmac` reads the (still-valid, since body is unchanged) HMAC header; `to_signable_string` returns the unchanged `raw_body`, so `HmacValidator.validate` returns `true`.
4. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)`.
5. Any host app logic keyed on `data.shop` (as shown in the gem's own documentation example) now processes attacker-supplied order/webhook data under the victim shop's tenant context.

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

**File:** docs/usage/webhooks.md (L19-29)
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
