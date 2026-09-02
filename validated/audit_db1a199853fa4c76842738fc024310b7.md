## Title
Webhook `shop` identity is trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that is handed to app webhook handlers from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, while the HMAC signature that `HmacValidator` verifies covers only the raw request body. This breaks the identity binding `signed_bytes == acted_on_identity`: the bytes that are cryptographically verified (`raw_body`) are not the same bytes that determine which shop/tenant the webhook payload is attributed to (`shop` header). Any request bearing a body+HMAC pair that is valid for the app's `client_secret` can be replayed with an arbitrary `shop-domain` header value and will be processed as if it originated from that (attacker-chosen) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from the `shop-domain` header, which is completely outside the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e. over `raw_body` only) and then, once that check passes, builds `WebhookMetadata` using `request.shop` — the same unauthenticated header — to identify the tenant for the downstream handler: [3](#0-2) 

`HmacValidator.validate` computes the HMAC solely from `verifiable_query.to_signable_string` (the body) and the app's shared secret; it never mixes in `shop`: [4](#0-3) 

Because the app's `client_secret`/`api_secret_key` is the same across every shop that installs the app, a body+HMAC pair that is valid for one shop's genuine webhook delivery is also a valid HMAC for the exact same body regardless of which `shop-domain` header accompanies it. This is the direct analog of the report's root cause: a field that is *acted on* (there, the option owner used for `closeAnytime`; here, the `shop` used to route/attribute the webhook payload) is not bound by the identity/authentication check (there, the signer check; here, the HMAC).

### Impact Explanation
An attacker who operates their own shop and has the app installed will legitimately receive real webhook deliveries (valid body + HMAC, since Shopify signs them with the app's secret) for their own shop. Because the `shop-domain` header is not part of the signed content, the attacker can resend the exact same body/HMAC pair to the app's webhook endpoint with a forged `shop-domain` header claiming it belongs to a different, victim shop. `Registry.process` will pass HMAC validation and hand `WebhookMetadata` with the attacker-chosen `shop` value to the app's handler. If the host application uses `WebhookMetadata#shop` (as intended/documented) to select which tenant's data/session to act on, this results in cross-tenant data confusion/corruption — e.g., the app could apply an `orders/create` or `app/uninstalled` payload against the wrong merchant's records, satisfying the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Exploitation requires the attacker to control (or previously operate) at least one shop with the target app installed so they can obtain one genuine signed webhook body/HMAC pair — no leaked secrets or privileged access are required, this is achievable by any unprivileged merchant. The header used to select the tenant is fully attacker-controlled at the HTTP layer and is never cross-checked against the signed payload, so the attack is a straightforward header substitution/replay once a valid signed body is obtained.

### Recommendation
Bind the tenant identity into the signed content used for verification, or otherwise cryptographically tie `shop` to the payload before it is trusted:
- Include the `shop` (and ideally `topic`/`webhook_id`) in the value passed to `HmacValidator`/`to_signable_string`, or
- Since Shopify's actual HMAC covers only the body by design, treat `request.shop` as merely a routing hint and require host applications to independently verify that the `shop` header matches a shop for which an active session/installation exists before acting on the payload, and document this requirement clearly in `Registry.process`/`WebhookMetadata`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook event (e.g. `orders/create`) so Shopify sends a genuine request to the app's webhook endpoint with body `B` and header `x-shopify-hmac-sha256: H`, computed as `HMAC-SHA256(client_secret, B)`.
2. Attacker captures this request and resends it to the same endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but replacing `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) using the app's `client_secret` and succeeds, since `H` is a valid signature for `B` regardless of the shop header. [5](#0-4) 
4. `request.shop` returns `victim-shop.myshopify.com`, and `WebhookMetadata` is built with that value and handed to the app's handler, which now processes attacker-controlled payload `B` as belonging to `victim-shop.myshopify.com`.

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
