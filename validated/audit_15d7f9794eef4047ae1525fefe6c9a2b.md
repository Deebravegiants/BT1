## Analysis

Mapping the reported bug class (an operation trusts an identity field that isn't covered by the same check that "proves" authenticity) onto this gem's webhook verification path surfaces a direct analog in `ShopifyAPI::Webhooks::Request` / `ShopifyAPI::Webhooks::Registry`. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook shop identity is not covered by the HMAC that authenticates the request, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `shop-domain` header to identify which merchant/tenant the payload belongs to when constructing `WebhookMetadata` for the handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) . `Utils::HmacValidator.validate` computes and compares an HMAC exclusively over that signable string, using the app's single, shop-independent `api_secret_key` [4](#0-3) . The `shop`, `topic`, and `webhook_id` values are read straight from HTTP headers and are never part of the signed bytes [5](#0-4) .

`Registry.process` then does:
```
raise ... unless Utils::HmacValidator.validate(request)
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))
``` [2](#0-1) 

Because `api_secret_key` is the same for every store that installs the app, any Shopify store owner can install the app on their own store, capture a real, validly-signed webhook for their own shop, and replay the exact same body to the app's webhook endpoint while swapping only the `x-shopify-shop-domain`/`shopify-shop-domain` header to a victim shop's domain. The signature check still passes (it only covers the body), so `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload came from the victim shop. This is precisely the "field acted on but not covered by the HMAC" pattern called out in the rules: `shop` is used to route/identify the tenant but is not bound by the same authenticator (`hmac`) that vouches for the payload's authenticity.

### Impact Explanation
An app that uses `data.shop` from the webhook handler to key its per-tenant data store (a normal, gem-sanctioned pattern — see `docs/usage/webhooks.md` guidance and `WebhookMetadata`) can be made to write, delete, or act on attacker-supplied data under a victim shop's identity — i.e., cross-tenant data corruption/access, using only a legitimately-issued webhook from the attacker's own (freely installable) store. This satisfies the Critical bar of "cross-tenant access."

### Likelihood Explanation
Any unprivileged internet user can install a public app on their own development/test store at no cost, generating a validly HMAC-signed webhook payload signed with the app's global `api_secret_key`. No credentials, tokens, or privileged access to the victim's account are required — only the ability to replay an HTTP request with a modified header, which is trivial.

### Recommendation
Bind the shop identity into the authenticated bytes, e.g., include `shop-domain` (and `topic`/`webhook-id`) in the HMAC-signed content, or require the resolved `shop` to be cross-checked against a shop-scoped session/secret before it is handed to `WebhookMetadata`. At minimum, document prominently that `request.shop`/`WebhookMetadata#shop` is unauthenticated and must never be trusted as a tenant boundary without an independent shop-session lookup.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a normal event (e.g. `orders/create`) so Shopify sends a real webhook to the app's endpoint, HMAC-signed with the app's `api_secret_key` over the JSON body.
2. Attacker captures this POST request (raw body + `x-shopify-hmac-sha256` header).
3. Attacker resends the identical body and HMAC header to the same webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks the (unmodified) raw body against the (unmodified) HMAC [6](#0-5) .
5. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`, and the host app processes attacker data under the victim tenant's identity.

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
