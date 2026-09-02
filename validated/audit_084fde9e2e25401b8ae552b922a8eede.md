### Title
Webhook `shop` and `topic` Fields Are Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` (and `topic`) values that the handler subsequently trusts are read from unauthenticated HTTP headers that are never included in the signed payload.

### Finding Description
`Webhooks::Request#hmac` is computed from the `shopify-hmac-sha256` header, and `#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

The `shop` value used downstream, however, is pulled straight from the `shopify-shop-domain` HTTP header, which is not part of the signed string: [3](#0-2) 

`Registry.process` validates only the HMAC over the body via `HmacValidator.validate(request)`, and — once that single check passes — dispatches the handler using `request.shop` (and `request.topic`) taken from those same unsigned headers: [4](#0-3) 

`HmacValidator.validate` itself only verifies `verifiable_query.to_signable_string` (the raw body) against the HMAC — it never incorporates `shop` or `topic`: [5](#0-4) 

This breaks the identity binding `HMAC-authenticated bytes == bytes the handler trusts as tenant identity`. In practice, all shops that install a given app share the same app `client_secret`, so a valid `(raw_body, hmac)` pair legitimately produced for one shop (e.g., an unprivileged user's own store where the app is installed) remains cryptographically valid for that same body regardless of which `shopify-shop-domain` header value accompanies it. An attacker who controls their own installation of the app can capture one legitimately-signed webhook body/HMAC pair and replay it against the app's webhook endpoint with an arbitrary `shopify-shop-domain` header (and/or `shopify-topic` header) of a different, victim tenant. The HMAC check still passes (it only checks the body), and `WebhookMetadata.shop`/`topic` passed to the app's handler will reflect the attacker-chosen victim shop: [6](#0-5) 

### Impact Explanation
This allows an unprivileged app installer (any merchant who can install the public app) to forge webhook events attributed to an arbitrary victim shop domain, tricking the host application into processing attacker-controlled data (order/customer/redact payloads, etc.) as if it originated from another tenant. This is a cross-tenant identity confusion at the library layer since the gem itself hands the host application a `shop` value that was never authenticated, directly matching the report's "identity binding broken via a field not covered by the HMAC" class.

### Likelihood Explanation
Exploitation requires only: (1) installing the public app once (no special privilege), (2) triggering any webhook delivery to capture one valid `(body, hmac)` pair for the attacker's own shop, and (3) POSTing that same body/HMAC to the app's public webhook endpoint with a forged `shopify-shop-domain`/`shopify-topic` header. No access to the app's `client_secret` or any merchant's access token is needed.

### Recommendation
Bind the `shop` (and `topic`) values into the HMAC-verified signable string, or otherwise cryptographically authenticate the header values (e.g., derive `shop`/`topic` only from a verified, out-of-band channel such as a signed callback URL, or require the host app to separately confirm the tenant via the delivered `webhook_id`/shop lookup before trusting header-sourced identity fields).

### Proof of Concept
1. Attacker installs the target public Shopify app on their own development shop `attacker.myshopify.com`.
2. Attacker triggers a webhook (e.g., `orders/create`) and captures the raw POST: body `B`, and headers including `shopify-hmac-sha256: H` (valid HMAC of `B` under the shared `client_secret`) and `shopify-shop-domain: attacker.myshopify.com`.
3. Attacker replays the exact same request to the app's webhook endpoint, only changing `shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `Registry.process` calls `HmacValidator.validate(request)` which only checks `H` against `B` — this still succeeds: [7](#0-6) 
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker data under the victim tenant's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
