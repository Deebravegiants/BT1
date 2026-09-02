### Title
Webhook shop-domain and topic headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
The reported Balancer bug shows a value used for accounting (`_reservesOf`) diverging from the value actually verified/trusted, letting an attacker exploit the gap. The same identity-binding gap exists in this gem's webhook processing: the HMAC signature only covers the raw request body, while the shop domain, topic, webhook id and API version headers — all fields the host application acts on for tenant identification — are never included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all read straight from HTTP headers, none of which are part of the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `HMAC(secret, to_signable_string)`, i.e. only the body: [3](#0-2) 

`Registry.process` checks only this body HMAC, then immediately trusts the unauthenticated headers to build `WebhookMetadata`, which is handed to the app's handler as the tenant identity for the event: [4](#0-3) 

The identity binding that should hold is:
`shop header used to route/scope the webhook == shop that produced (and is authenticated by) the signed bytes`

But since the signature only binds the body, this equality does not hold: `shop` (and `topic`, `webhook_id`, `api_version`) can be swapped freely while keeping a body+HMAC pair valid for *any* shop that shares the same app `api_secret_key` — which is every shop that installs the app, since the same app-level secret signs every shop's webhooks.

### Impact Explanation
An unprivileged internet user who can install the app on their own (attacker-owned) shop can capture a genuine `raw_body` + `x-shopify-hmac-sha256` pair from a real webhook delivery to their own endpoint. Because the HMAC secret (`api_secret_key`) is shared across all shops for a given app, and the signature never covers `x-shopify-shop-domain` or `x-shopify-topic`, the attacker can replay that same body/HMAC to the victim app's webhook endpoint while forging the `x-shopify-shop-domain` header to a victim shop domain (and/or the `x-shopify-topic` header to a sensitive topic such as a data-erasure or uninstall topic). `Registry.process` will accept it as valid and dispatch `WebhookMetadata` with the forged `shop`/`topic` to the host application's handler, causing the app to act on the wrong tenant — a cross-tenant integrity/confidentiality violation (e.g., misattributed data writes, deletions, or GDPR-erasure actions against a shop the attacker does not own).

### Likelihood Explanation
Reachable by any unprivileged actor able to install the target app once (a normal, permissionless action on Shopify) and send crafted HTTP requests to the app's public webhook endpoint — no leaked secrets, tokens, or privileged access required. The only "skill" needed is capturing one legitimate webhook delivery to their own shop and replaying it with modified headers, which is a low bar.

### Recommendation
Include the security-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the payload (e.g., verify `shop` against a value embedded in the signed body, or require the host app to cross-check the header shop against session/tenant records before trusting `WebhookMetadata#shop`). Document clearly that the current signature only authenticates the body and that headers must not be relied upon for tenant identification without further verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers an `orders/create` webhook, capturing `raw_body` and the resulting `x-shopify-hmac-sha256` value (both are legitimately produced by Shopify with the app's shared `api_secret_key`).
2. Attacker POSTs the same `raw_body` to the app's webhook endpoint, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: shop/redact` (or any topic registered by the app)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only — this matches, so validation passes: [5](#0-4) 
4. The handler registered for the forged topic is invoked with `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"`, even though the request was never authenticated for that shop or topic.

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
