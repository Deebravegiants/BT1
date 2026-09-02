### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts an *unauthenticated* `shop-domain` header to attribute the payload to a tenant. Because the HMAC binds only to the body bytes and not to the shop identity, a request that carries a legitimately-signed body (for shop A) can have its `shop-domain` header swapped to shop B, and the gem will accept it as authentic and dispatch it to the host app's handler labeled as shop B.

### Finding Description
`Registry.process` verifies authenticity like this: [1](#0-0) 

The HMAC check delegates to `Utils::HmacValidator.validate`, which computes the signature purely from `verifiable_query.to_signable_string`: [2](#0-1) 

For a webhook `Request`, `to_signable_string` returns only the raw HTTP body — it does not include the `shop`, `topic`, `webhook_id`, or `api_version` fields: [3](#0-2) 

`shop` is instead derived directly from the `x-shopify-shop-domain` (or `shopify-shop-domain`) header, with no cryptographic binding to the signed body: [4](#0-3) 

After HMAC validation succeeds, `Registry.process` builds `WebhookMetadata` using that same unauthenticated `request.shop` value and hands it to the host application's handler as the tenant identity for the event: [5](#0-4) [6](#0-5) 

This is exactly the identity-binding break called out in the analog criteria: **a field acted on (`shop`, used by the host app as the tenant key) but not covered by the HMAC**. Contrast this with `Auth::Oauth::AuthQuery`, used in the OAuth callback flow, where `shop` *is* included inside `to_signable_string` and therefore *is* bound by the HMAC: [7](#0-6) 

So the gem's own OAuth path treats `shop` as security-critical and signs it, while the webhook path deliberately (or by oversight) excludes it from the signed material, despite the app using it identically — as the tenant-scoping key passed into user handler code.

### Impact Explanation
Because the api_secret_key used to compute the webhook HMAC is shared across *all* shops that have installed the app, any attacker who can obtain one validly-HMAC'd body+signature pair (e.g., by legitimately triggering a webhook on their own store, which they fully control and can inspect) can replay that exact body/HMAC pair while substituting an arbitrary victim shop's domain in the `x-shopify-shop-domain` header. `HmacValidator.validate` will accept it — it never inspects the header. `Registry.process` will then pass `WebhookMetadata` with the attacker-chosen `shop` value to the host app's handler, which typically uses `shop` to look up/scope the tenant's data (e.g., "update order status for shop X"). This is a cross-tenant confusion primitive: an attacker-controlled payload can be injected and attributed to a shop they do not own, corrupting or forging data under another merchant's identity within any host application that relies on this gem's webhook shop attribution without independently re-verifying tenancy.

### Likelihood Explanation
Moderate. The prerequisite — obtaining one authentic webhook body+HMAC pair — is trivial for any attacker who installs the target app on their own (attacker-controlled) shop and triggers any webhook event (e.g., `orders/create` with attacker-chosen order content). The endpoint is public-facing (it must accept unauthenticated POSTs from "Shopify"), and nothing in this gem prevents replaying the captured body/HMAC with a forged `shop-domain` header. The main mitigating factor is that many webhook bodies contain shop-specific identifiers (e.g., resource IDs, GIDs) that a downstream handler *might* cross-check against `shop`, but the gem itself provides no such protection and nothing in the interface (`WebhookHandler#handle`) signals to implementers that `data.shop` is unauthenticated relative to `data.body`.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the HMAC-verified signable string for webhook requests, mirroring what `Auth::Oauth::AuthQuery#to_signable_string` already does for the OAuth callback. At minimum, document prominently that `WebhookMetadata#shop` is not covered by the HMAC and must not be trusted as a tenant boundary unless independently corroborated by the payload body.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body `B` and the resulting `x-shopify-hmac-sha256` header value `H`, which Shopify computed as `HMAC_SHA256(api_secret_key, B)`.
2. Attacker crafts a new HTTP request to the app's webhook endpoint with:
   - Body: the same `B`
   - `x-shopify-hmac-sha256: H` (unchanged, still valid because HMAC only covers `B`)
   - `x-shopify-shop-domain: victim.myshopify.com` (swapped from `attacker.myshopify.com`)
   - `x-shopify-topic`, `x-shopify-webhook-id` set as desired
3. `ShopifyAPI::Webhooks::Request.new` parses these headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC_SHA256(api_secret_key, B) == H`, per `lib/shopify_api/utils/hmac_validator.rb:26-31` and `lib/shopify_api/webhooks/request.rb:35-38`.
4. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: JSON.parse(B), ...))`, per `lib/shopify_api/webhooks/registry.rb:198-199`.
5. The host application's handler now processes attacker-supplied body content under the victim shop's identity, since it received `shop: "victim.myshopify.com"` from a call that passed HMAC validation.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
