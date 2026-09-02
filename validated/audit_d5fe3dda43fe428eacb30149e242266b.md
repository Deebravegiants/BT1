### Title
Webhook HMAC signature does not cover the `shop-domain` header, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature over the raw request body only, while the `shop` value used to route and identify the webhook is read from an unauthenticated HTTP header. Any actor who can obtain one genuinely-signed webhook body (e.g., by installing the app on their own store) can replay that exact body to the app's webhook endpoint while forging the `X-Shopify-Shop-Domain` header to name a victim shop, and the signature check will still pass.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, however, is taken straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is not part of that signable string: [2](#0-1) 

`Registry.process` validates the HMAC over the body, then immediately trusts `request.shop` (from the unauthenticated header) to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` only ever authenticates `verifiable_query.to_signable_string` against `verifiable_query.hmac`: [4](#0-3) 

Because the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is the same for every shop that installs the app, the signature over a given body is valid regardless of which shop it is replayed under. The identity binding that is broken is:

`shop authenticated by HMAC` (nothing — shop isn't in the signed payload) vs. `shop trusted and acted upon by the handler` (`request.shop`, from an attacker-controllable header).

### Impact Explanation
An attacker who installs the vulnerable app on their own store receives genuinely HMAC-signed webhook bodies for that store (e.g. `orders/create`, `customers/data_request`, `shop/redact`). They can capture one such body/HMAC pair and POST it to the app's shared webhook endpoint with the `shop-domain` header rewritten to a victim shop. `Utils::HmacValidator.validate` still returns `true` since the signature only covers the body, and `Registry.process` will invoke the app's webhook handler believing the event originates from the victim shop, with attacker-chosen JSON content. Depending on how the host app's handler uses `WebhookMetadata#shop` (e.g., looking up the victim's stored session/access token, writing to the victim's tenant record, or triggering data-redaction/order logic against the victim), this results in cross-tenant data corruption or cross-tenant action execution — data or actions belonging to one merchant are attributed to another merchant's tenant context.

### Likelihood Explanation
Any developer/attacker can freely obtain a real app installation on their own store (or a trial/dev store) and thus mint arbitrarily many valid `(body, hmac)` pairs signed with the app's shared `client_secret`. No access token, session, or credential belonging to the victim is required — only knowledge of the app's public webhook endpoint URL, which is typically public. This makes the attack straightforward for any unprivileged internet user who can install the target app.

### Recommendation
Bind the shop identity into the authenticated material: include the `shop-domain` (and ideally `webhook-id`/`api-version`) header value in `to_signable_string`, or otherwise verify that the shop named in the header corresponds to a session/installation record independently established via OAuth for that specific webhook delivery, before trusting `request.shop` in `Registry.process`.

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) to receive a real `raw_body` and its `X-Shopify-Hmac-SHA256` value, both signed with the app's `client_secret`.
2. Send a POST to the app's webhook endpoint with:
   - Body: the captured `raw_body` (unmodified)
   - Header `X-Shopify-Hmac-Sha256`: the captured signature (unmodified)
   - Header `X-Shopify-Shop-Domain`: `victim.myshopify.com` (forged)
   - Header `X-Shopify-Topic`: same topic as captured
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` because `to_signable_string` only checks `raw_body`, which is unmodified.
4. `Registry.process` dispatches to the app's handler with `WebhookMetadata#shop == "victim.myshopify.com"`, even though the payload actually originated from the attacker's own store.

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
