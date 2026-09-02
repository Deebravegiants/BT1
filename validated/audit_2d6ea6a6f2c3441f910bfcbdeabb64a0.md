### Title
Webhook shop attribution is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook only by verifying the HMAC signature over the raw request body. The `shop` value that is subsequently passed to the app's webhook handler (and typically used by the host application to key data updates, deletions, or side effects) is read straight from the unauthenticated `x-shopify-shop-domain` HTTP header and is never part of the signed data.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Webhooks::Registry.process` validates the HMAC over that signable string and, once it passes, immediately trusts `request.shop` (sourced from the `x-shopify-shop-domain`/`shopify-shop-domain` header) to build the `WebhookMetadata` handed to the app's handler: [2](#0-1) 

The `shop` accessor itself is a plain header read with no cryptographic binding to the signed body: [3](#0-2) 

`Utils::HmacValidator.validate` only compares the computed signature of `to_signable_string` (the raw body) against the received `hmac`: [4](#0-3) 

The identity binding that should hold is: `shop that produced/authorized the signed body == shop the app attributes the event to`. Because the header carrying the second value is excluded from the signed bytes, the two sides of that equality are never compared. Any entity capable of obtaining one valid `(raw_body, hmac)` pair — for example a normal merchant who legitimately receives webhooks for their own store, an unprivileged actor from this gem's threat perspective relative to other tenants — can replay that exact body/signature pair while swapping only the `x-shopify-shop-domain` header to any victim shop domain. `HmacValidator.validate` will still return `true` because it never looks at that header, and the host application's handler will process the payload as though it originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the HMAC check is supposed to enforce: `Utils::HmacValidator.validate(request)` returning `true` is presented as a guarantee that the request (including which shop it concerns) is authentic and came from Shopify for that shop, but the shop attribution is unauthenticated. A host application that keys any state (order sync, inventory, subscription status, uninstall handling, GDPR data erasure, etc.) off `WebhookMetadata#shop` can be made to apply another tenant's data to the wrong tenant, or apply attacker-controlled data under a victim shop's identity — a cross-tenant access/data-integrity violation reachable purely through this gem's documented `Registry.process` API, with no access token, secret, or privileged account required.

### Likelihood Explanation
Exploitation only requires possession of a single legitimate `(raw_body, hmac)` pair for one's own shop (trivially obtainable by any app-installing merchant/attacker sending themselves a webhook-triggering event) plus the ability to set an arbitrary `x-shopify-shop-domain` header value when delivering the forged HTTP request to the app's webhook endpoint — no cryptographic secret or additional credential is needed since the header is entirely outside the signed content.

### Recommendation
- Bind the shop identity into the verified data: either include `shop-domain` (and `topic`) in the HMAC signable string used by `Webhooks::Request#to_signable_string`, or require the app/gem to independently confirm that the header-derived `shop` matches an expected/registered shop for the delivered `topic`/`webhook_id` before dispatching to the handler.
- At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be trusted for tenant-keyed side effects unless corroborated by other means, and consider raising in `Registry.process` if the shop header cannot be corroborated against a known installation.

### Proof of Concept
1. Attacker registers/owns "attacker-shop.myshopify.com" and installs the target app, which registers a webhook handler for topic `orders/create`.
2. Attacker triggers a real order event on their own shop; Shopify sends the app a genuine webhook request with body `B` and header `x-shopify-hmac-sha256: H` (a valid signature over `B` computed with the app's secret) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays this exact request to the app's webhook endpoint but changes only `x-shopify-shop-domain` to `victim-shop.myshopify.com`, keeping body `B` and header `H` unchanged.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only (`Webhooks::Request#to_signable_string` returns `@raw_body`) and successfully matches `H`.
5. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: parsed_body_of_B, ...)`, causing the app to process attacker-controlled order data as if it belonged to `victim-shop.myshopify.com`.

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
