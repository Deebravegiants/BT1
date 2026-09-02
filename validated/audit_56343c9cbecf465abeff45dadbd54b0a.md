This confirms the finding: `HmacValidator` uses the single app-wide `Context.api_secret_key` for all webhook verification [1](#0-0) , and `Webhooks::Request#to_signable_string` only covers `@raw_body`, never the `shop-domain` header [2](#0-1) . This is a valid analog under the "field acted on but not covered by the HMAC" rule.

### Title
Webhook shop identity spoofing via unauthenticated `shop-domain` header — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body alone, while the `shop` (from the `x-shopify-shop-domain`/`shopify-shop-domain` header) is read out-of-band and never included in the signed material. `Registry.process` validates only that the *body bytes* were HMAC-signed by the app's single, shop-agnostic `Context.api_secret_key`, then forwards the attacker-controllable `shop` value straight into `WebhookMetadata` for the handler to act on as the tenant identity.

### Finding Description
`HmacValidator.validate` verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, Context.api_secret_key)` [3](#0-2) . For webhooks, `to_signable_string` returns only `@raw_body` [4](#0-3) . The `shop` accessor, however, is read directly from the `shopify-shop-domain` header with no cryptographic binding to the signature at all [5](#0-4) .

`Registry.process` raises only if the body-HMAC check fails, then immediately constructs `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` and dispatches it to the host application's handler [6](#0-5) . Because `Context.api_secret_key` is the single app-wide client secret used to validate webhooks for *every* shop that installs the app (not a per-shop secret), the equality the library implicitly claims to enforce — `shop asserted in header == shop that produced/owns this signed body` — is never actually checked. Documentation explicitly tells developers that `data.shop` is "The shop domain of the webhook" [7](#0-6) , encouraging host apps to trust it as the tenant key (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` as shown in the same doc [8](#0-7) ).

This is the same class of bug as the report: a downstream computation trusts a value (`transferParameter.to_` walked back into `tokenStorage.ledger`, i.e. an identity reused across two roles) instead of the value actually verified/updated in the same operation. Here, the verified quantity (raw body bytes, under an app-wide secret) is not the quantity the handler keys its tenant-scoped side effects on (`shop` header).

### Impact Explanation
Any entity capable of installing the app on **any single shop** (a normal unprivileged merchant/developer store) receives genuinely Shopify-signed webhook deliveries — valid `raw_body` + `hmac` pairs computed with the app's one global `api_secret_key`. Because the `shop-domain` header is not covered by that signature, the attacker can replay the exact same signed body while substituting an arbitrary `x-shopify-shop-domain` value (e.g., a victim shop that also has the app installed). `Registry.process` will accept it as valid and hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop. If the host application uses `data.shop` to select which tenant's records to create/update/delete (the documented, expected usage pattern), this enables cross-tenant data injection or corruption — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Requires only that the attacker run the app on their own store (a normal, low-privilege install) to obtain a validly-signed body/HMAC pair, then replay it to the app's webhook endpoint with a forged `shop-domain` header. No access to `api_secret_key`, tokens, or any privileged account is needed, and this is entirely reachable through the gem's own documented `Registry.process`/`Request` API.

### Recommendation
**Short term:** Have `Registry.process` (or `Request`) cross-check `request.shop` against the caller-supplied list/registry of shops known to have this webhook registered (or require callers to pass an expected shop and compare) before dispatching to the handler, rather than trusting the unsigned header outright.

**Long term:** Extend `VerifiableQuery`/`to_signable_string` for webhooks to incorporate the shop identity into the value that's checked against expectations (even though Shopify's own HMAC doesn't cover it), and update `docs/usage/webhooks.md` to explicitly warn that `data.shop` is unauthenticated and must be validated against the app's known-installed-shops list before being used as a tenant key.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggers a webhook (e.g. `orders/create`), and captures the raw POST body plus the genuine `X-Shopify-Hmac-Sha256` header — both valid under the app's single `api_secret_key`.
2. Attacker resends the identical body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts it (all required headers present) [9](#0-8) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the raw body against the app-wide secret [10](#0-9) .
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes/persists data as if it legitimately came from the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
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
