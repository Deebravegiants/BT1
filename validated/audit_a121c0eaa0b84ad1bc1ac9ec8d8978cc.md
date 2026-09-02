### Title
Webhook `shop-domain` Header Is Not Bound By The HMAC Signature, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity solely by HMAC-checking the raw request body, but the `shop` value passed to the app's handler is read from the `X-Shopify-Shop-Domain` HTTP header, which is never included in the signed material. This breaks the intended identity binding `HMAC-verified bytes == data trusted by handler`; the `shop` field acted upon by the handler is not covered by the HMAC.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it against the `hmac-sha256` header value: [1](#0-0) 

For webhooks, `Request#to_signable_string` returns only the raw request body: [2](#0-1) 

Meanwhile, `Request#shop` is derived entirely from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic tie to the body or the HMAC: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately forwards `request.shop` to the app's handler as the trusted tenant identifier, without any additional check that the header matches the shop that actually produced the signed body: [4](#0-3) 

Because the HMAC only binds the body bytes, an attacker who controls their own Shopify development store can:
1. Trigger a legitimate webhook from their own shop (`attacker-shop.myshopify.com`), obtaining a body + a valid HMAC signed with the app's `client_secret` for that body.
2. Replay the identical request to the app's webhook endpoint, but rewrite the `X-Shopify-Shop-Domain` header to point at a victim shop (`victim-shop.myshopify.com`).
3. `Utils::HmacValidator.validate` still passes, because the signature only ever covered the raw body, not the header.
4. `Registry.process` calls the handler with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)`, so the app processes attacker-supplied data as if it belonged to the victim tenant.

This is exactly the "shop authenticated versus the shop acted upon" identity-binding break: the equality that should hold is `hmac_verified_source_shop == shop_used_by_handler`, but the gem currently guarantees only `hmac_verified(body) == true` while `shop` is taken from unverified header bytes.

### Impact Explanation
Any app that uses `WebhookMetadata#shop` to key persistent state (e.g., to look up a merchant session/access token, write to per-shop records, or trigger merchant-scoped side effects) can be made to act on data for shop A while attributing it to shop B. This is a cross-tenant data integrity/confidentiality issue: an attacker-controlled shop can inject webhook payloads that the app associates with a victim shop it does not control, without needing the victim's credentials or the app's `client_secret`.

### Likelihood Explanation
The attacker only needs their own free/development Shopify store (not the app's `client_secret`, not the victim's access token) to obtain one validly-signed webhook body, then can freely relabel the `shop-domain` header on replay. No privileged access, TLS interception, or social engineering is required — only network access to the app's public webhook endpoint and control of a shop that can install/trigger webhooks for the same app. This is a realistic, unprivileged-internet-user attack path.

### Recommendation
Bind the shop identity into the material that is HMAC-verified, or otherwise cryptographically tie the `shop-domain` header to the verified body — e.g., include the resolved shop domain (and ideally topic/webhook-id) in the signable string used by `HmacValidator`, or require the host application to independently verify that `request.shop` corresponds to a shop with an active installation/session before trusting it in `WebhookMetadata`. At minimum, document prominently that `request.shop` is unauthenticated and must not be trusted for tenant-scoping decisions without an additional installation/session lookup.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own store and captures a real webhook:
#    body = '{"id": 123, ...}'
#    headers = {
#      "x-shopify-hmac-sha256" => "<valid HMAC for `body` using the app's real client_secret>",
#      "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
#      "x-shopify-topic" => "orders/create"
#    }

# 2. Attacker replays the identical body+HMAC but swaps the shop header:
headers["x-shopify-shop-domain"] = "victim-shop.myshopify.com"

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true, because it only checks `body`.
# => The registered handler receives WebhookMetadata with shop: "victim-shop.myshopify.com",
#    even though the payload actually originated from the attacker's own shop.
``` [4](#0-3) [5](#0-4)

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
