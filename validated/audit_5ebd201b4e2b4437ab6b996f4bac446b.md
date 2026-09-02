### Title
Webhook shop identity spoofing via replay — HMAC covers only the raw body, not the `X-Shopify-Shop-Domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop` from an HTTP header that is never included in the HMAC-signed material, so a party who possesses one legitimately-signed webhook payload can replay it with a forged shop header and have it accepted as coming from a different shop.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`: [1](#0-0) 

The signable content used for that HMAC check is exclusively the raw request body: [2](#0-1) 

`HmacValidator.validate_signature` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it against the `hmac` accessor, i.e. it authenticates the body bytes only: [3](#0-2) 

`request.shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header and is never covered by `to_signable_string`, nor cross-checked against anything derived from the signed body: [4](#0-3) 

That unauthenticated `shop` value is then handed directly to the application's webhook handler as the tenant identity for the event: [5](#0-4) 

**Binding broken (as an equality):**
`signer_of(raw_body) == owner_of(shop_header)` is assumed by every handler that trusts `WebhookMetadata#shop`, but the gem only proves `signer_of(raw_body) == "the app's configured secret was used"`. It proves nothing about the `shop` header, because `shop` is not part of `to_signable_string`.

Before attack: `(raw_body_A, hmac_A, shop=A)` — valid, correctly attributes to shop A.
After attacker's replay: `(raw_body_A, hmac_A, shop=B)` — `HmacValidator.validate` still returns `true` (body/HMAC pair untouched), but `request.shop == "B"`, a shop the attacker does not own.

### Impact Explanation
Any actor who can obtain one legitimately HMAC-signed webhook body for their own shop (e.g., any merchant who installs the app and triggers a normal event such as `orders/create` or `app/uninstalled`) can replay that exact body to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header of any other shop. Because the api_secret_key is shared across all tenants of the app (it is the app's secret, not a per-shop key), the same signed payload is "valid" for every shop the app serves. The application's handler will process the event as if it came from the victim's shop — enabling cross-tenant data confusion or state corruption (e.g., a forged `app/uninstalled` for shop B triggering deletion of shop B's session/data, or forged business-data webhooks being persisted under the wrong shop). This is a cross-tenant identity-binding bypass, matching the Critical impact bucket (cross-tenant access) even though it requires only body-and-signature material the attacker legitimately owns for their own shop.

### Likelihood Explanation
Reachable by any unprivileged internet user who can install the app on a shop they control (or otherwise capture one legitimately delivered webhook), with no need for `api_secret_key`, an access token, TLS interception, or social engineering. The only requirement is the ability to send an arbitrary HTTP request with attacker-chosen headers to the app's public webhook endpoint, which is by design internet-reachable.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) into the signed material, or otherwise verify the header-derived `shop` against an independent, trusted source (e.g., look up the session/shop record first and reject if inconsistent with any shop identifier the app already trusts for that installation) before invoking the handler in `ShopifyAPI::Webhooks::Registry.process`. At minimum, document that consuming applications must not treat `WebhookMetadata#shop` as authenticated unless corroborated by an out-of-band trusted mapping (e.g., only accept webhooks for a shop that already has a currently active app installation session), and consider making the registry itself enforce this rather than delegating it silently to callers.

### Proof of Concept
1. Attacker installs the app for `attacker-shop.myshopify.com` and triggers any webhook (e.g., updates a product to fire `products/update`). They capture the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent.
2. Attacker resends that exact body and HMAC header to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, raw_body)` — unaffected by the shop header change: [1](#0-0) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-controlled `body`, and acts on it as if it were an authentic event from the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
