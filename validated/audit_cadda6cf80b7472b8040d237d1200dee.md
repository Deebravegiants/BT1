### Title
Webhook shop identity is not bound to the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, then unconditionally trusts the `shop-domain` header — which is never covered by that HMAC — as the tenant identity passed to the app's handler. This is the same class of defect as the reported bug: a value used to make a security/business decision (`maxEnforcedTick`'s pool-identity binding) is derived from data that is not actually validated against the value it's supposed to correspond to.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/verifies the HMAC exclusively over `to_signable_string`: [2](#0-1) 

Meanwhile `Request#shop` simply reads an attacker-influenceable header with no cryptographic linkage to the signed body: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately forwards `request.shop` — the unverified header — into `WebhookMetadata` handed to the app's handler, with no secondary check that the shop header corresponds to the body/signature: [4](#0-3) 

Since the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is shared across every shop that installs the app — it is not shop-specific — any actor who has installed the app on a shop they control (a normal, unprivileged action, not requiring leaked credentials or an access token) will legitimately receive Shopify-signed webhook requests for that shop. Because the signature only binds the JSON body and never the `shop-domain` header, that actor can replay/forward such a request to the app's webhook endpoint with the `shop-domain` header rewritten to point at an arbitrary victim shop. `HmacValidator.validate` will still return `true` (the body and signature are untouched), and `Registry.process` will pass the forged `shop` value straight to the app's `WebhookHandler`, which the documentation explicitly tells integrators to treat as "The shop domain of the webhook": [5](#0-4) 

This breaks the equality that should hold: `shop authenticated by the HMAC == shop consumed by the handler`. Instead, `shop consumed by the handler` is fully attacker-controlled while `shop authenticated by the HMAC` is effectively nothing (the HMAC binds only the body, not the sender's identity).

### Impact Explanation
Any downstream logic that keys off `WebhookMetadata#shop` (job dispatch, per-shop data updates, mandatory privacy webhooks such as `shop/redact`, `customers/redact`, `customers/data_request`, or triggering `app/uninstalled` cleanup) can be invoked by an attacker for a shop they do not operate, using their own legitimately-issued webhook signature. This is a cross-tenant access/identity-spoofing primitive: the attacker forges the app's belief about which merchant an event pertains to, without ever possessing that merchant's credentials, access token, or the app's `client_secret`.

### Likelihood Explanation
Exploitation only requires: (1) installing the target app on an attacker-controlled development/test store (an ordinary, unprivileged action available to anyone), (2) capturing one legitimately Shopify-signed webhook request, and (3) resending it to the app's public webhook endpoint with a modified `shop-domain`/`x-shopify-shop-domain` header. No secret material, TLS interception, or social engineering is needed, making this straightforward for any internet user who can install the target Shopify app.

### Recommendation
Bind the shop identity into the authenticated material before trusting it: either (a) include the `shop-domain` header value in the HMAC-signable string so the signature covers shop+body together, or (b) require callers of `Registry.process`/`WebhookHandler` to cross-check `request.shop` against an independently-verified session/store record (e.g., only accept webhooks for shops with an active, previously-established session) rather than trusting the header outright.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com` and trigger any registered webhook topic (e.g. `orders/create`); capture the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sends — this HMAC is computed with the app's single, shop-independent `client_secret`.
2. Replay that exact body and HMAC header to the app's webhook endpoint, but change `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the (untouched) body against the (untouched) HMAC: [6](#0-5) 
4. The app's `WebhookHandler#handle` is invoked with `data.shop == "victim-shop.myshopify.com"`, even though the request never actually originated from or was authorized by that shop.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
