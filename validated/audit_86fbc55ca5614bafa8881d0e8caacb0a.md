This confirms the finding. The gem's documented webhook API (`ShopifyAPI::Webhooks::Registry.process` / `ShopifyAPI::Webhooks::WebhookHandler#handle`) is exactly what apps are told to use per `docs/usage/webhooks.md` and `BREAKING_CHANGES_FOR_V15.md`, and it hands `shop` (and `topic`, `webhook_id`, `api_version`) to the handler as trusted, HMAC-verified identity, even though none of these header-derived fields are covered by the HMAC.

### Title
Webhook HMAC only covers the request body, letting an attacker forge the `shop` (tenant) identity delivered to app handlers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook by checking `Utils::HmacValidator.validate(request)`, which only verifies `request.to_signable_string`, i.e. the raw HTTP body [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` values consumed by the app come entirely from HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`, etc.) that are never part of the signed content [2](#0-1) . `Registry.process` passes these unauthenticated header values straight to the app's handler as `WebhookMetadata`, alongside the body whose integrity was actually checked [3](#0-2) .

### Finding Description
The binding that should hold is: `hmac == HMAC(secret, body || shop || topic)`, i.e. the merchant/tenant identity claimed by the request should be cryptographically bound to the same signature that authenticates the payload. Instead, `HmacValidator.validate_signature` computes `OpenSSL::HMAC.hexdigest(secret, verifiable_query.to_signable_string)` and compares it only to the `hmac` header [4](#0-3) , and `Request#to_signable_string` returns only `@raw_body` [1](#0-0) .

Because the app's registered HMAC secret (`Context.api_secret_key`) is the app's single `client_secret`, shared across every shop that installs the app, any unprivileged attacker who installs the app on their own store receives legitimately-signed webhook deliveries `(body, hmac)` for their own shop. Since `shop-domain`, `topic`, `webhook-id`, and `api-version` are plain headers outside the signed content, that attacker can replay the exact same `(raw_body, hmac)` pair directly to the app's public webhook endpoint while substituting any `shop-domain` header value they like (e.g. a victim shop's domain) and even a different `topic`/`webhook-id`. `Registry.process` will still find `Utils::HmacValidator.validate(request)` to be true - because it only re-validates the body - and will dispatch `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` to the handler as if these fields were authenticated [5](#0-4) .

App handlers are documented (`BREAKING_CHANGES_FOR_V15.md`, `docs/usage/webhooks.md`) to trust `data.shop` as the tenant identifier for looking up sessions/access tokens and processing the webhook body under that shop's scope. This breaks the identity binding `shop_verified_by_hmac == shop_used_by_handler`: the shop actually covered by the signature (none, since only body is signed) is not the shop the handler is told to act on behalf of.

### Impact Explanation
This allows cross-tenant impersonation: an attacker who is an unprivileged installer of the target app on their own shop can cause the app to process attacker-controlled webhook bodies while the app believes the event originated from an arbitrary different shop domain of the attacker's choosing. Depending on the handler's logic (e.g. syncing order/product/customer data, revoking access, updating billing state keyed by `data.shop`), this can lead to cross-tenant data corruption or disclosure keyed to a shop the attacker does not control, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
The prerequisite - installing the app on one's own store to receive at least one legitimately signed webhook - is available to any unprivileged internet user who can install a public app, and no access token, `client_secret`, or privileged account is required. The header fields are trivially attacker-controlled once the attacker can POST directly to the app's public webhook route with a previously captured `(body, hmac)` pair.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`/`api_version`) into the signed content, or otherwise cryptographically tie the header-derived identity to the verified payload before constructing `WebhookMetadata`, e.g. by requiring an out-of-band, per-shop verified webhook subscription id/secret, or by rejecting mismatches between the HMAC-covered payload and header claims where feasible. At minimum, document loudly that `data.shop`/`data.topic` are not authenticated by the HMAC check and must not be trusted for tenant-scoping without additional verification (such as confirming the shop has an active, matching session/webhook registration).

### Proof of Concept
```ruby
# 1. Attacker installs the target app on their own shop "attacker.myshopify.com"
#    and receives a legitimate webhook delivery for, say, "orders/create":
raw_body   = '{"id":1,"note":"hi"}'
valid_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_client_secret, raw_body)
)

# 2. Attacker replays the same (body, hmac) pair directly to the app's public
#    webhook endpoint, but swaps the shop-domain header for a victim shop:
forged_headers = {
  "x-shopify-topic"       => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,          # still valid! only body is signed
  "x-shopify-shop-domain" => "victim.myshopify.com", # attacker-chosen, unauthenticated
  "x-shopify-webhook-id"  => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate(request) returns true (body/hmac match),
#    handler.handle(data: WebhookMetadata(shop: "victim.myshopify.com", ...)) is invoked,
#    even though "victim.myshopify.com" never sent this webhook.
```

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
