## Title
Webhook `shop-domain` header is not covered by the HMAC, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from HTTP headers that are never included in that signed value. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then unconditionally trusts `request.shop` as the tenant identity handed to the host app's handler. This breaks the binding "shop authenticated == shop the data belongs to," letting anyone who legitimately receives a webhook for their own (attacker-controlled) shop replay that same body/HMAC pair while spoofing the `shop-domain` header to impersonate a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated headers: [2](#0-1) 

`Registry.process` validates only that the HMAC matches the body, then immediately builds `WebhookMetadata` using `request.shop` as the trusted tenant identifier passed to the app's handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only ever hash `verifiable_query.to_signable_string` (the raw body for webhooks) against the app's secret — the shop header plays no role in the signature: [4](#0-3) 

Because Shopify computes the HMAC purely over the JSON body with the app's shared secret, and the gem never binds that body to a specific shop, the equality the code implicitly assumes — `hmac-verified body ⇒ shop-domain header is authentic` — does not hold. Any merchant who has installed the app (an unprivileged, non-credentialed party from the app's perspective) receives real webhook deliveries containing a valid `body` + `hmac` for their own shop. They can resend that exact `body`/`hmac` pair to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header (e.g., a victim shop they don't own), and `Registry.process` will accept it as valid and dispatch it to the handler tagged with the attacker-chosen shop.

### Impact Explanation
This is a cross-tenant identity-binding break: an app relying on `WebhookMetadata#shop` (or `request.shop`) to determine which merchant's records a webhook affects can be made to apply attacker-supplied webhook data under a different, unrelated shop's identity. Any host app following the gem's own documented pattern (dispatch handler using `data.shop`) inherits this weakness with no way to detect the forgery, since the library itself asserts the request passed HMAC validation.

### Likelihood Explanation
Any actor who has installed the target app on their own store — no special privilege, no leaked secret, no access token needed — automatically receives legitimate `body`/`hmac` pairs for every webhook topic they subscribe to, and can immediately replay them with a modified shop header. This requires no interaction with the victim and no timing race, unlike the analog report's self-transfer requirement.

### Recommendation
Bind the shop identity into the verified material: either include the `shop-domain` (and `topic`/`webhook_id`) header in the HMAC-signable string, or independently verify, on the host-app side and inside `Registry.process`, that `request.shop` corresponds to a shop for which the app actually holds an installed/active session before dispatching the handler. At minimum, document prominently that `request.shop` is unauthenticated and must be cross-checked against known installed shops before use.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` and registers for a webhook topic (e.g. `orders/create`).
2. Shopify delivers a webhook to the app with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid hmac of body>`, and some JSON `body`.
3. Attacker captures this `body` and `x-shopify-hmac-sha256` value, then sends their own POST to the app's webhook endpoint, keeping `body` and `hmac` unchanged but setting `x-shopify-shop-domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only re-computes the HMAC over `request.to_signable_string` (`@raw_body`) — unaffected by the header change — so validation succeeds: [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop == "victim.myshopify.com"`, even though the payload actually originated from the attacker's own shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
