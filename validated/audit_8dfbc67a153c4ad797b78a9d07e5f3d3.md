### Title
Webhook `shop` (tenant) identity is not bound to the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook purely by validating the HMAC of the raw request body, but the `shop` value that is subsequently used to identify the tenant (and handed to the app's webhook handler) is read from an HTTP header that is never part of the signed data. This breaks the identity binding `HMAC-authenticated bytes == bytes acted on for tenant scoping`, allowing a party who can obtain any one genuine `(raw_body, hmac)` pair (e.g. by installing the app on their own store and capturing a legitimate webhook delivery) to replay that pair while swapping the `x-shopify-shop-domain`/`shopify-shop-domain` header to claim the payload belongs to a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is populated straight from the (attacker-controllable, from the perspective of a replayed request) header, with no cryptographic linkage to the body or to the HMAC: [2](#0-1) 

`HmacValidator.validate` verifies only `verifiable_query.to_signable_string` (i.e., the raw body) against the HMAC computed with the app's shared `api_secret_key`: [3](#0-2) 

`Registry.process` uses this same HMAC check as the sole authentication gate, then immediately forwards the unauthenticated `request.shop` value to the handler as the tenant identifier: [4](#0-3) 

Because Shopify signs webhook bodies using the app's single, app-wide `client_secret` (not a per-shop secret), any merchant who has installed the app on a store they control receives genuine `(body, hmac)` pairs that are valid under that same secret. Nothing in this gem ties a particular `(body, hmac)` pair to the specific `shop-domain` header it originally arrived with — the header is trusted verbatim for tenant identification and is completely outside the signed content. An attacker who has legitimately received one webhook for their own shop can therefore resend the identical body and HMAC to the app's webhook endpoint while substituting the victim's shop domain in the header, and `Registry.process` will treat it as an authentic webhook for the victim shop.

### Impact Explanation
This is a cross-tenant access vulnerability (Critical per the given impact list): a party with no privilege in the victim's shop can cause the host application to process webhook data under the victim shop's identity, since `WebhookMetadata#shop` (built directly from `request.shop`) is what apps typically use to look up per-tenant sessions/records and drive shop-scoped side effects. Depending on the handler's logic, this can lead to acting on/against another merchant's tenant data using a forged provenance claim.

### Likelihood Explanation
Requires only the ability to install the target app on any store (which is normally open to any merchant/developer, i.e., an "unprivileged internet user" relative to the victim shop) and network access to replay an HTTP POST to the app's public webhook endpoint. No access token, `api_secret_key`, or credential theft is required — only reuse of a legitimately received, validly-signed payload with a substituted header.

### Recommendation
Bind the shop identity into the authenticated material, e.g. include `shop-domain` (and ideally `webhook-id`/`api-version`) in `to_signable_string`, or independently verify the header-derived shop against a shop value embedded in the verified payload/metadata before it is passed to handlers. At minimum, document and enforce that consumers must cross-check `data.shop` against an already-known, previously-established session/shop record rather than trusting it as ambient truth.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, a store they control.
2. Attacker triggers a webhook event (e.g. `orders/create`) and captures the raw body and the `x-shopify-hmac-sha256` header Shopify sent to the app's webhook endpoint — this HMAC is valid because it's computed with the app-wide `api_secret_key`, not a shop-specific key.
3. Attacker resends an HTTP request to the app's webhook endpoint with the identical raw body and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the headers, `HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC, and `Registry.process` invokes the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, per: [4](#0-3) 
5. The host application processes attacker-controlled data as if it originated from the victim's shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
