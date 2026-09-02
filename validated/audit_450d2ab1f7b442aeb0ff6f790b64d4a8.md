### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `ShopifyAPI::Webhooks::Registry.process` uses the unauthenticated `shop-domain` header (via `request.shop`) as the tenant identity passed to the host app's webhook handler. The HMAC therefore proves the body's integrity/origin but never binds it to a specific shop, breaking the identity equality `hmac_signed_bytes == bytes_the_app_trusts_for_tenant_identity`.

### Finding Description
`ShopifyAPI::Webhooks::Request` derives `shop` straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [1](#0-0) 

But the value that is HMAC-verified is only the raw body: [2](#0-1) 

`Registry.process` validates the HMAC and then hands `request.shop` straight to the app's handler as the authoritative tenant identifier, with no cross-check that the signed body actually originated for that shop: [3](#0-2) 

Contrast this with `ShopifyAPI::Auth::Oauth::AuthQuery`, where `shop` **is** included in `to_signable_string` and therefore is bound by the HMAC: [4](#0-3) 

Because the same `api_secret_key` is shared across all shops installed on the app (there is no per-shop signing key), any (body, hmac) pair that is valid for one shop's webhook remains cryptographically valid regardless of which `shop-domain` header accompanies it. The documented handler contract explicitly trusts `data.shop` as the shop this webhook is "for": [5](#0-4) [6](#0-5) 

### Impact Explanation
An attacker who legitimately installs the app on their own store (an unprivileged, ordinary merchant/internet user relative to other tenants) receives real, correctly-signed webhook deliveries for their own shop from Shopify. They can capture one such `(raw_body, hmac)` pair — the body is attacker-controlled content in most topics (e.g. `orders/create`, `customers/create`) — and replay that exact body+HMAC to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` only checks that the body matches the secret-keyed HMAC, so validation passes, and `Registry.process` invokes the app's handler with `WebhookMetadata.shop` set to the victim's domain and attacker-controlled `body`. This lets the attacker inject data, trigger business logic, or corrupt state that the host application attributes to another tenant — a cross-tenant integrity/identity-binding break within the scope of this gem's own webhook verification code, satisfying the "cross-tenant access" impact category.

### Likelihood Explanation
Any app developer that installs the gem on multiple shops is exposed as soon as one malicious merchant installs the app. No access token, `client_secret`, or privileged access is required — only the ability to install the app (a normal, unprivileged action) and send an HTTP POST to the app's public webhook endpoint with attacker-chosen headers, which is trivial for anyone who knows the callback path (often documented/predictable, e.g. `callback/orders/create`).

### Recommendation
Include the tenant-identifying header(s) (`shop-domain`, and ideally `topic`/`webhook-id`) in the HMAC-signed content of `ShopifyAPI::Webhooks::Request#to_signable_string`, or otherwise verify server-side that the HMAC-covered payload is consistent with the `shop-domain` header before exposing `request.shop` to `WebhookHandler#handle`. At minimum, document/enforce that host apps must independently verify the `shop` claim (e.g., against a known installed-shop list) before trusting `WebhookMetadata#shop`, and consider deriving/comparing shop identity from a value that is cryptographically bound to the delivery.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, satisfying OAuth normally.
2. Shopify sends a legitimate webhook to the app's endpoint:
   - Headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-topic: orders/create`
   - Body: attacker fully controls order content via their own store actions (e.g., crafts an order with attacker-chosen `note`, `email`, line items, etc.).
3. Attacker intercepts/replays this exact `(raw_body, hmac)` pair in a new POST to the same app endpoint, only changing the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this into a request object; `Utils::HmacValidator.validate` recomputes HMAC over `raw_body` only [7](#0-6)  and it matches, since the header was never part of the signed input.
5. `Registry.process` calls the app handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-crafted-json>, ...)` [8](#0-7) , so the host application processes attacker-controlled data as if it belonged to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** docs/usage/webhooks.md (L12-18)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

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
