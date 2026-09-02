### Title
Webhook shop attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop-domain` header — which is never part of the signed material — to attribute the payload to a merchant.

### Finding Description
`Webhooks::Request` implements `VerifiableQuery` and defines its signable content as only the raw body: [1](#0-0) 

The `shop` accessor is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, completely outside the signed payload: [2](#0-1) 

`HmacValidator.validate` computes the signature exclusively from `to_signable_string` (i.e., the body) and compares it against the `hmac` header: [3](#0-2) 

`Registry.process` uses this same validation and then forwards `request.shop` — the unauthenticated header — directly into the metadata passed to the app's webhook handler, without any additional binding check between the verified body and the claimed shop: [4](#0-3) 

Because the app's webhook HMAC secret (`Context.api_secret_key` — the app's `client_secret`) is shared across every shop that has installed the app, any merchant who has installed the app can trigger a webhook containing attacker-influenced content addressed to their own shop, capture the resulting valid `(body, hmac)` pair, and then replay that exact body/HMAC to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `HmacValidator.validate` will report success (the body signature is genuinely valid), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop — an identity binding break: **shop verified by HMAC ≠ shop acted upon by the handler**.

### Impact Explanation
Any code path in the host application keyed off `WebhookMetadata#shop` (e.g., looking up the shop's session/access token, updating shop-scoped records, or triggering shop-owner notifications) can be made to act on behalf of a shop the attacker does not control, using data the attacker fully crafted. This is a cross-tenant confused-deputy condition entirely reachable through this gem's own `Registry.process`/`HmacValidator` logic, without needing any credentials beyond having a shop that has legitimately installed the target app.

### Likelihood Explanation
Any merchant that installs an app using this gem can generate arbitrary webhook bodies for their own shop (e.g., by creating/updating resources whose fields are echoed into webhook payloads) and capture the resulting valid HMAC. Replaying it against the same publicly reachable webhook endpoint with a forged `shop-domain` header requires no special access, making this readily exploitable by any app-installing shop owner.

### Recommendation
Bind the `shop` (and ideally `topic`/`api_version`) claim to the HMAC-verified material, e.g., include the `shop-domain` header value in `to_signable_string`'s HMAC input, or perform a secondary integrity check comparing the header-provided shop against a value embedded in the signed body/session lookup before dispatching to the handler. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be trusted as a tenant boundary without further verification (e.g., cross-checking against a shop for which the app holds a valid, previously issued access token).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and legitimately receives a webhook whose body they control the content of (e.g., a product/order webhook containing attacker-chosen text fields), together with its valid `X-Shopify-Hmac-SHA256` value computed over that body using the app's `client_secret`.
2. Attacker resends that exact raw body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the HMAC over `@raw_body` [5](#0-4)  — validation succeeds since the body/HMAC pair is genuine.
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)` [6](#0-5)  and the host application processes attacker-controlled data as though it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
