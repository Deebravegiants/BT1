## Vulnerability Analog Found

### Title
Webhook shop attribution is not covered by the HMAC signature, enabling cross-tenant shop spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates its HMAC over the raw request body only, while the `shop` value that is subsequently trusted and handed to app webhook handlers is read from an unauthenticated HTTP header. This breaks the identity binding `shop_authenticated == shop_acted_on`, mirroring the reported bug class where an unprotected field (`FeeGranter`) is trusted for actions instead of the value actually bound by the signature (`FeePayer`).

### Finding Description
`Request#hmac` and `Request#to_signable_string` derive the HMAC exclusively from the raw JSON body: [1](#0-0) [2](#0-1) 

`HmacValidator.validate` only checks `to_signable_string` (i.e., the raw body) against the HMAC secret — it never incorporates `shop`, `topic`, or `webhook_id`: [3](#0-2) 

Meanwhile, `Request#shop` is read straight from the `x-shopify-shop-domain` / `shopify-shop-domain` header with no cross-check against the signed payload: [4](#0-3) 

`Registry.process` validates only the HMAC, then forwards the attacker-controllable `request.shop` value directly into `WebhookMetadata` given to the app's handler: [5](#0-4) 

Because the signature never binds `shop` (or `topic`/`webhook_id`) to the body, any party who can produce one genuinely-signed `(body, hmac)` pair — trivially obtainable by subscribing their own store to a webhook topic that yields a fixed/predictable body (e.g., an empty-body topic) — can replay that exact `body`+`hmac` pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` still passes because it only checks the body bytes, yet the handler receives `data.shop` set to the attacker-chosen shop domain.

### Impact Explanation
This is a cross-tenant identity-binding bypass: the value the app is meant to trust as "which shop this webhook is about" (`shop`) is not the value actually authenticated by the HMAC (the raw body). Any app that keys database writes, cache invalidation, uninstall/deauthorization logic, or session revocation off `WebhookMetadata#shop` can be made to perform those actions against an arbitrary victim shop's tenant, using only a self-obtained genuine signature over a fixed/predictable body. This matches the report's "Critical/High - cross-tenant access" impact bucket, since no credentials of the target tenant are required — only knowledge of the app's own `api_secret_key`-signed traffic from the attacker's own store.

### Likelihood Explanation
Exploitation requires no privileged access to the target tenant: the attacker only needs (1) their own development/trial store to legitimately trigger any webhook whose body is fixed or guessable (many topics, e.g. `app/uninstalled`, ship an empty `{}` body), giving them a valid `(body, hmac)` pair for the shared `api_secret_key`, and (2) the ability to POST to the target app's public webhook endpoint with a forged `shop-domain` header. Both are reachable by an unprivileged internet user with no leaked credentials or social engineering.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the signed payload check, or require the app-layer to independently verify that `request.shop` corresponds to a shop with an active, previously-established session/installation before trusting it — the gem should document/enforce that `shop` from headers must not be treated as authenticated by the HMAC alone. At minimum, provide a helper that validates the signature is being checked in tandem with a known/allow-listed shop domain the app expects, rather than exposing raw unauthenticated header data as the tenant identifier passed to handlers.

### Proof of Concept
1. Attacker registers a webhook (e.g., `app/uninstalled`) on their own store `attacker-shop.myshopify.com`. Shopify sends: body `{}`, header `x-shopify-hmac-sha256: <valid HMAC over "{}">`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays this exact body and HMAC header to the victim app's public webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` recomputes HMAC over `to_signable_string` (`"{}"`) and it matches — validation passes.
4. `Registry.process` invokes the app handler with `WebhookMetadata.new(topic: "app/uninstalled", shop: "victim-shop.myshopify.com", ...)`, causing the app to run its uninstall/deauthorization logic against `victim-shop`, a tenant the attacker never authenticated against.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
