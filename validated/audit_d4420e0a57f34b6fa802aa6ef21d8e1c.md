### Title
Webhook `shop` domain is trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by validating an HMAC that covers only the raw request body, yet it hands the caller-supplied `shop-domain` header — which is *not* covered by that HMAC — to the host application as the authoritative tenant identifier. Anyone who installs the target app on a shop they control receives their own legitimately HMAC-signed webhooks (the HMAC key is the app's single shared `client_secret`, identical across every installing shop) and can replay the exact same `(body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header, causing the host application to process the payload under a victim shop's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC solely over `verifiable_query.to_signable_string`, i.e. only the body, and compares it to the received `hmac-sha256` header: [2](#0-1) 

`Registry.process` validates that HMAC and then, on success, builds `WebhookMetadata` directly from `request.shop`, which is parsed straight from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header: [3](#0-2) [4](#0-3) 

Because the HMAC key (`Context.api_secret_key`) is the same for every shop that installs the app — not per-shop — any unprivileged attacker can install the app on their own store, capture a genuine `(raw_body, hmac-sha256)` pair from a real webhook delivery for their own shop, and then send that identical pair to the app's webhook endpoint while setting `shopify-shop-domain` (or `shopify-topic`/`webhook-id`) to a value of their choosing. `Utils::HmacValidator.validate` will still pass, because it never inspects the shop header, and `Registry.process` will hand the forged `shop` value to the registered handler as trusted `WebhookMetadata#shop`.

This breaks the identity binding that host applications rely on: `shop header used to select/mutate tenant data == shop that actually produced the signed payload`. The gem asserts authenticity of the body/topic but silently omits the shop from that assertion, despite `WebhookMetadata` presenting `shop` as if it were verified.

### Impact Explanation
Any application built on this gem that uses `WebhookMetadata#shop` (as returned to webhook handlers) to look up or mutate per-shop records — the normal, documented usage pattern — can be made to apply an attacker-controlled shop's legitimate webhook payload to an arbitrary victim shop's tenant data. This is a cross-tenant access/write vulnerability: an attacker who installs the app on their own store can trigger actions (e.g., order/webhook side effects, cache invalidation, data deletion flows keyed by shop) against a shop they do not own, without ever obtaining that victim's credentials.

### Likelihood Explanation
Likelihood is high: obtaining a valid `(body, hmac)` pair only requires installing the target app on an attacker-owned development/trial store — an ordinary, unprivileged action available to any internet user — after which the attacker can freely relay the captured request to the app's public webhook endpoint with a modified shop header. No secrets, tokens, or privileged access from the victim are required.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the data that is cryptographically bound to the request before it is trusted, e.g. by validating `request.shop` against the shop associated with the session/registration that the webhook is being processed for, or by requiring host applications to cross-check `WebhookMetadata#shop` against an independently verified shop (such as one derived from a session lookup) rather than treating the header as authenticated by `HmacValidator.validate`. At minimum, document prominently that `WebhookMetadata#shop` is not covered by the HMAC and must not be trusted as an identity boundary on its own.

### Proof of Concept
1. Attacker creates a Shopify development store and installs the target app (any unprivileged user can do this).
2. Attacker registers/observes a normal webhook delivery to their own store's endpoint, capturing the raw JSON body and the `x-shopify-hmac-sha256` header value — both valid because they were legitimately signed with the app's shared secret for the attacker's own shop.
3. Attacker replays that exact `(raw_body, hmac)` pair to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC: [5](#0-4) 
5. `Registry.process` invokes the host application's handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, and the host application performs actions against `victim-shop.myshopify.com`'s data, believing the webhook was authenticated for that shop.

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
