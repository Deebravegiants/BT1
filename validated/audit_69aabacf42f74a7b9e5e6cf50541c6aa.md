### Title
Webhook shop identity spoofing via unauthenticated `X-Shopify-Shop-Domain` header not covered by HMAC - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The webhook `HMAC` signature validated by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body, never the `shop-domain` header. Since a single app's `client_secret` (`Context.api_secret_key`) is shared across *every* merchant shop that has installed the app, any attacker who controls one legitimate installation can capture a validly-signed webhook payload from their own shop and replay it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header pointing at a victim shop. The HMAC check still passes, and `Webhooks::Registry.process` hands the handler a `WebhookMetadata` object whose `shop` is taken directly from the forged, unauthenticated header.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no cryptographic binding to the signed body: [2](#0-1) 

`HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string`, i.e., the body only: [3](#0-2) 

`Registry.process` trusts this unauthenticated `request.shop` value directly when constructing the metadata passed to the app's handler: [4](#0-3) 

Because `Context.api_secret_key` is the same `client_secret` for the app across all of its installed shops (it is not shop-scoped), an attacker who owns one legitimate shop installation can:
1. Trigger any webhook topic on their own shop (they fully control this, e.g. by editing an order, or even by triggering `customers/data_request`/`app/uninstalled` themselves), capturing the raw body and its valid `X-Shopify-Hmac-Sha256` value.
2. Replay that exact `(body, hmac)` pair to the app's webhook endpoint, substituting `X-Shopify-Shop-Domain` with an arbitrary victim shop's domain.
3. `HmacValidator.validate` succeeds because it only checks the body bytes against the shared secret; the `shop` field is never part of the equality it enforces.

This breaks the intended identity binding: `hmac verified ⇒ (body, shop) authentic`, when in reality only `hmac verified ⇒ body authentic for some shop of this app`. The `shop` an app relies on to select tenant-scoped session/data (`WebhookMetadata#shop`) is attacker-controlled.

### Impact Explanation
This is a cross-tenant confusion vector: an attacker-controlled webhook body (with attacker-chosen topic and payload) can be delivered to the app labeled as belonging to a different, victim shop. Depending on how the host app's `WebhookHandler` uses `data.shop`/`data.body` (e.g., looking up the victim's stored offline session/access token to act on their behalf, writing/mutating records keyed by shop, or triggering mandatory compliance topics like `customers/redact`/`shop/redact` against a shop the attacker doesn't own), this enables cross-tenant data pollution or triggering of privileged, shop-scoped actions using the victim's own stored access token — satisfying the "cross-tenant access" Critical impact class.

### Likelihood Explanation
The attacker only needs a legitimate (even trial/free) installation of the target app on any shop they control — no access to `client_secret`, tokens, or credentials of the victim is required, since the signing secret is shared across all shops for the given app. Constructing and replaying an HTTP POST with a modified header is trivial once one authentic `(body, hmac)` pair is captured.

### Recommendation
Bind the `shop` identity into the HMAC-verified material, or otherwise authenticate it independently of the raw body: e.g., verify the delivered `shop-domain` header against the shop the app actually has an active session/webhook subscription for the given `webhook_id`/topic combination before trusting it, and/or require Shopify's webhook `X-Shopify-Webhook-Id` to be looked up against the app's own registered subscriptions per shop instead of trusting the header verbatim.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" with the app installed.
# 1. Trigger any webhook (e.g. orders/create) on their own shop, capture:
raw_body = '{"id": 1, "note": "malicious payload"}'
valid_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_CLIENT_SECRET, raw_body)
)

# 2. Replay to the app's webhook endpoint with a forged shop header:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,       # still valid: body unchanged
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, unauthenticated
  "x-shopify-webhook-id" => "attacker-controlled-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (body/hmac match),
#    handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
```

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
