### Title
Webhook shop identity is not covered by the HMAC signature, enabling cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then unconditionally trusts the `x-shopify-shop-domain` header to identify which tenant/shop the payload belongs to. Because the shop identifier is never included in the HMAC-signed material, the equality "shop the HMAC authenticates" == "shop the handler acts on" does not hold, allowing a request with a validly-signed body to be relabeled to any shop domain of the attacker's choosing.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw JSON body — it never includes the shop domain, topic, or any other header: [2](#0-1) 

The `shop` value that is later handed to the application's handler is read straight from the `x-shopify-shop-domain` / `shopify-shop-domain` header, a value that is completely outside the HMAC's coverage: [3](#0-2) 

`Registry.process` validates the HMAC and, once it passes, immediately trusts `request.shop` (and other unsigned headers) to build the `WebhookMetadata` that is dispatched to the host application's handler — with no additional binding check between the authenticated body and the claimed shop: [4](#0-3) [5](#0-4) 

Because the webhook HMAC secret (`Context.api_secret_key`) is per-app, not per-shop, any merchant who has installed the app (i.e., an "unprivileged internet user" from the app's perspective, requiring no special access) can obtain genuinely-signed webhook deliveries for their own shop. A valid `(body, hmac)` pair authenticates only the body — it says nothing about which shop it came from. An attacker who can get such a pair accepted by the app's public webhook endpoint (replaying/forwarding it with a modified `x-shopify-shop-domain` header) causes the receiving application to process the payload under an arbitrary victim shop's identity, since the gem enforces no cryptographic link between the two.

### Impact Explanation
This breaks the identity binding "the shop attested by the signed payload" == "the shop the application acts on," letting one tenant's authenticated webhook content be attributed to a different tenant. Any app logic keyed off `WebhookMetadata#shop` (e.g., looking up the victim's session/access token, updating the victim's stored data, or triggering shop-scoped side effects) can be manipulated by a merchant using its own legitimately-signed webhook traffic, resulting in cross-tenant data confusion/injection.

### Likelihood Explanation
Moderate-to-high: exploitation requires the attacker to install the app on a shop they control (a normal, unprivileged action) to obtain genuinely HMAC-signed webhook deliveries, and then to relay a request to the app's public webhook endpoint with the shop header altered. No secrets, tokens, or privileged access are required beyond the ability to install the app and send an HTTP request — both are attacker-controlled.

### Recommendation
Bind the shop identity into the value actually verified, e.g., include the shop domain (and topic/webhook id) inside the HMAC-signable string, or independently corroborate `request.shop` against a value obtained through an already-authenticated channel (such as the shop associated with the specific webhook subscription/topic combination) before constructing `WebhookMetadata`. At minimum, document in the gem that `WebhookMetadata#shop` is not itself covered by the HMAC and must not be trusted as a sole tenant identifier without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com`, becoming a legitimate merchant of the app.
2. Shopify sends the attacker's shop a real webhook: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, header `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures this request and resends it to the app's public webhook endpoint, only changing `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes `HMAC(secret, B)` from the unmodified body and confirms it matches — validation succeeds because the shop header was never part of `to_signable_string`. [6](#0-5) 
5. `Registry.process` builds `WebhookMetadata.new(..., shop: request.shop, ...)` with `shop == "victim.myshopify.com"` and dispatches it to the app's handler, which now processes attacker-controlled body content under the victim shop's identity. [7](#0-6)

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
