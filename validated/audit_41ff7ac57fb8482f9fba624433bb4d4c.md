Confirmed: the webhook HMAC only covers the raw body via `Request#to_signable_string` returning `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated headers [2](#0-1) . `Registry.process` validates only the HMAC of the body, then trusts `request.topic` and `request.shop` from headers to dispatch to a handler and populate `WebhookMetadata` [3](#0-2) . Documentation confirms host apps are expected to use `data.shop` to identify which tenant/merchant the webhook belongs to [4](#0-3) .

### Title
Webhook Shop/Topic Headers Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, never including the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers. `Registry.process` accepts any request whose body HMAC validates against the app's shared `api_secret_key`, then trusts the unauthenticated `shop` and `topic` headers to dispatch and to populate `WebhookMetadata` passed to the host application's handler.

### Finding Description
The identity binding that should hold is: `HMAC_valid(body) == authentic(shop, topic, webhook_id, api_version, body)`. In this gem it only holds for `body`:

- `Request#to_signable_string` returns `@raw_body` exclusively [1](#0-0) .
- `Request#shop`, `#topic`, `#webhook_id`, `#api_version` are read straight from HTTP headers with no cryptographic binding to the signed body [2](#0-1) .
- `HmacValidator.validate` only ever calls `verifiable_query.to_signable_string`, so it can never detect header tampering [5](#0-4) .
- `Registry.process` gates only on this body-only HMAC check, then forwards the attacker-controlled `topic`/`shop` headers straight into `WebhookMetadata`, which is documented as the value host apps use to key their per-merchant data [3](#0-2) [4](#0-3) .

Critically, `api_secret_key` (the app's client secret used to sign webhook bodies) is shared by Shopify across **every merchant** that installs the app — it is not shop-specific. Any unprivileged internet user can become a genuine merchant on a public app (e.g., installing a free/dev-store instance of the app) and thereby legitimately receive webhooks whose bodies are validly HMAC-signed with that same shared secret. Because headers are excluded from the signature, that same person can replay the captured `(body, valid-hmac)` pair to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header (a victim's shop) and/or `topic` header. `Registry.process` will accept it as authentic and hand the forged `shop` value to the handler, which typically uses it to look up/update per-tenant records — a cross-tenant integrity violation.

### Impact Explanation
This breaks the equality `authenticated_shop == handler_trusted_shop`. Since `shop` is the tenant-identifying field used by host applications (per this gem's own documented usage pattern) to select which merchant's data to mutate, an attacker who legitimately owns one merchant account for the app can forge webhook deliveries that appear to originate from a different, victim shop and/or under a different topic than what was actually signed. This is a cross-tenant access primitive achievable by any internet user with access to the app's public webhook callback URL and one legitimate install, without needing the app's `client_secret` or any victim credentials.

### Likelihood Explanation
High feasibility: the webhook callback path is a public HTTP endpoint reachable by any internet user; obtaining a valid `(body, hmac)` pair requires nothing more than installing the app on an attacker-controlled/dev shop, which many public apps allow freely; replaying with modified headers requires only a basic HTTP client.

### Recommendation
1. Include `shop`, `topic`, and `webhook_id` in the HMAC-signed payload (`to_signable_string`) so header tampering invalidates the signature, matching how `Auth::Oauth::AuthQuery#to_signable_string` binds all relevant fields [6](#0-5) .
2. Where the signed payload cannot be changed (Shopify controls the wire format), have `Registry.process` cross-check the `shop` header against the shop that the specific webhook subscription was registered for (tracked server-side per subscription/topic) before invoking the handler, rather than trusting the header value unconditionally.

### Proof of Concept
1. Attacker installs the target app on an attacker-controlled shop `attacker.myshopify.com`, receiving a legitimate webhook, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker sends a POST to the app's public webhook callback endpoint with the same body `B` and same `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (and optionally a different `X-Shopify-Topic`).
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` [7](#0-6) .
4. `Registry.process` looks up the handler by the attacker-supplied `topic` and calls `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", ...))` [3](#0-2) .
5. The host application's handler processes the forged webhook believing it is authentic data for `victim.myshopify.com`, corrupting or leaking that tenant's data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
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

**File:** docs/usage/webhooks.md (L12-29)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

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
