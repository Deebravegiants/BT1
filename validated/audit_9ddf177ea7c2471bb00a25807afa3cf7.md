Confirmed: `Utils::VerifiableQuery` requires only `hmac` and `to_signable_string`, and `Webhooks::Request#to_signable_string` returns only `@raw_body`. All identity metadata (`shop`, `topic`, `webhook_id`, `api_version`) is read from HTTP headers that are never part of the signed bytes. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook `shop` identity is taken from an unauthenticated header, not bound by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the `shop` (and `topic`/`webhook_id`/`api_version`) values pulled straight from HTTP headers to build the `WebhookMetadata` passed to the app's handler. Because the HMAC only covers `@raw_body`, the header-derived `shop` value is never cryptographically bound to the signature that authenticated the request, breaking the equality `authenticated_shop == hmac_signed_bytes.shop`.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over whatever `to_signable_string` returns and compares it to the `hmac` field of the object implementing `Utils::VerifiableQuery`: [4](#0-3) 

For webhooks, `Webhooks::Request#to_signable_string` returns only the raw JSON body: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers, which are not part of the HMAC-signed material at all: [5](#0-4) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the authenticated tenant identity, forwarding it to the app's handler: [3](#0-2) 

Since Shopify signs webhooks with the app's single `client_secret` (shared across every shop that installs the app), the HMAC only proves "this body was signed by our app's secret for *some* shop" — it does not prove which shop. An unprivileged attacker who has installed the app on their own store receives genuine webhook deliveries (raw body + valid HMAC) addressed to their own shop. They can replay that exact `raw_body`/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with a victim shop's domain. `Utils::HmacValidator.validate` still succeeds (the body/HMAC pair is genuinely valid), and `Registry.process` calls the app's handler with `shop: <victim's domain>` even though the payload content actually belongs to the attacker's own shop.

This is the same class of bug as the referenced report: a value acted upon (`shop`, used as the tenant identity) is not covered by the integrity check (HMAC over `raw_body` only), letting an attacker sever the binding between the signature and the identity it's supposed to authenticate.

### Impact Explanation
This breaks cross-tenant isolation: a malicious merchant/user of the shared app can cause the host application to process attacker-supplied webhook content under a different (victim) shop's identity. Depending on how the host app's `WebhookHandler` uses `data.shop` (e.g., looking up/updating per-shop records, triggering per-shop side effects), this allows tenant confusion/cross-tenant data injection — a Critical-class impact (cross-tenant access) achievable by an unprivileged attacker who merely installed the app once.

### Likelihood Explanation
Likelihood is moderate-to-high for any app that has at least one other install (the attacker's own store) and exposes a webhook endpoint built on this gem's `Webhooks::Registry`/`Webhooks::Request`. No access token, `client_secret`, or privileged access is required — only the ability to receive one legitimate webhook to one's own shop and replay it with a modified header to the shared endpoint.

### Recommendation
Include the tenant/identity-relevant header fields (`shop-domain`, `topic`, `webhook_id`, `api_version`) in the signed material used for HMAC verification, or otherwise cryptographically bind the shop identity to the payload before trusting `request.shop`. At minimum, `to_signable_string` should not be limited to `@raw_body` when other fields (`shop`, `topic`, etc.) are later trusted as authenticated by callers.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; attacker triggers an event (e.g., updates a product) causing Shopify to send a genuine webhook to the app's endpoint with headers `shopify-shop-domain: attacker-shop.myshopify.com`, a real `raw_body`, and a valid `shopify-hmac-sha256`.
2. Attacker captures this `raw_body` + HMAC pair (they control their own endpoint/logs).
3. Attacker POSTs the identical `raw_body` and HMAC to the app's webhook endpoint again, but replaces the `shopify-shop-domain` header with `victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC [6](#0-5) .
5. `WebhookMetadata.new(... shop: request.shop ...)` is built with `shop == "victim-shop.myshopify.com"` [7](#0-6) , and the app's handler processes attacker-controlled body content under the victim's shop identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
