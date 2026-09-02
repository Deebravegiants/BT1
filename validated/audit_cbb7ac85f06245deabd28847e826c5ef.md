### Title
Webhook shop identity is not covered by the HMAC signature, allowing shop-domain spoofing across tenants - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC over the raw request body only, but then dispatches the handler using the `shop`, `topic`, `webhook_id`, and `api_version` values taken from unauthenticated HTTP headers. Because those header fields are not part of the signed bytes, an attacker who possesses one valid (body, HMAC) pair for their own shop can freely swap the `shop-domain` (and other) headers to claim the webhook belongs to a different merchant, and the HMAC check still passes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over that signable string and compares it to the `hmac-sha256` header: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` trusts this HMAC check as proof of authenticity for the whole request, then builds `WebhookMetadata` using `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all of which are read straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) and are never included in the HMAC-covered bytes: [3](#0-2) [4](#0-3) 

This breaks the intended identity binding: `authenticated(raw_body) == acted_on(shop, topic, webhook_id, api_version)`. In reality only `raw_body` is authenticated; `shop` and the other header-derived fields are attacker-controlled and unauthenticated. Any application that trusts `WebhookMetadata#shop` (or `#topic`/`#webhook_id`) to select which merchant's session/data/state to update is vulnerable to cross-tenant confusion: a merchant who has installed the app (and thus can trigger genuine webhook deliveries containing their own valid body+HMAC) can replay that exact body/HMAC pair while substituting `x-shopify-shop-domain` for a victim shop domain, and the gem will report it as an authenticated webhook for the victim shop.

This is the same root-cause pattern as the report's random-index example: a value is trusted/acted upon (`winnerIndex`/`shop`) that is not actually constrained by the mechanism assumed to guarantee its correctness (`pot.numParticipants`/the HMAC).

### Impact Explanation
This allows cross-tenant access: an attacker (any merchant with the app installed, i.e. an "unprivileged" party relative to other tenants) can make the host application process attacker-supplied webhook data attributed to an arbitrary victim shop domain, without possessing the app's `client_secret` or any victim credentials. Depending on how the consuming application uses `WebhookMetadata#shop`, this can lead to writing/deleting data or triggering business logic against the wrong merchant account, satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is high for any app that installs the library as documented: the attacker only needs a Shopify store where they've installed the target app (a normal, low-privilege action), which lets them receive at least one legitimately signed webhook whose body they can inspect, then replay it with a forged `shop-domain` header. No secret material needs to be leaked; the attack works purely because the gem's `to_signable_string` for webhooks omits header fields from the signed payload.

### Recommendation
Include the shop domain (and ideally topic/webhook-id/api-version) in the HMAC-covered signable string for webhooks, or independently verify that `request.shop` corresponds to a shop with an active session/installation before trusting it in `WebhookMetadata`. At minimum, document prominently that `Request#shop` is unauthenticated and must be cross-checked by the host application against a known installed shop before use.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, triggering a legitimate webhook delivery with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker captures this request and re-sends it to the app's webhook endpoint, changing only the header `x-shopify-shop-domain` to `victim-shop.myshopify.com` (headers are excluded from `to_signable_string`, so the HMAC is unaffected).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only — the check succeeds because `B` and the HMAC were untouched: [5](#0-4) 
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, even though the request never touched Shopify's servers for that shop.

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
