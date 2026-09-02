### Title
Webhook Shop Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying an HMAC over the raw request body, but the `shop` (tenant identity) field that is handed to the app's webhook handler is read from an HTTP header that is never included in the signed material. This breaks the intended binding `hmac == HMAC(secret, body)` ⟺ `shop == authenticated_sender`, allowing an unprivileged holder of any one valid `(body, hmac)` pair to relabel that payload as originating from an arbitrary other shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` values are all read from separate HTTP headers that are not part of the signed string: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` (the body only), and then constructs the handler payload directly from the unauthenticated `request.shop` header: [3](#0-2) 

`HmacValidator.validate` computes and compares the signature purely over `verifiable_query.to_signable_string`: [4](#0-3) 

Because the app-wide webhook signing secret (`Context.api_secret_key`) is the same for every shop that installs the app, any merchant who has installed the app can legitimately trigger a webhook delivery for their own shop and thereby obtain a genuine `(raw_body, hmac)` pair. Since the `shop-domain` header carrying the tenant identity is excluded from the signed string, that same `(raw_body, hmac)` pair remains valid when replayed to the app's webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header changed to any other shop the attacker chooses. `HmacValidator.validate` still returns `true` because the body is unchanged, and `Registry.process` will dispatch the handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop domain, even though the payload content actually originated from the attacker's own shop.

This is exactly the "field acted on but not covered by the HMAC" identity-binding break: the equality the design intends is `authenticated_tenant == request.shop`, but the code only proves `authenticated_body == request.body`, leaving `request.shop` completely attacker-controlled.

### Impact Explanation
This is a cross-tenant access vulnerability. An application relying on `WebhookMetadata.shop` (as returned by `Registry.process`) to determine which tenant's data to read, write, or delete will act on the wrong tenant's records using attacker-supplied header values, despite the HMAC check passing. An attacker who merely operates their own install of the vulnerable host app (an unprivileged, non-credentialed party with respect to any other merchant) can forge webhook deliveries that are misattributed to any other shop, letting them inject fabricated events (e.g., order/customer/app-uninstall data) against a victim tenant's account within the host application. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any host application that installs the app on more than one shop (the normal multi-tenant SaaS model for a Shopify app). The attack requires no special privileges — signing up as a regular merchant and installing the app is sufficient to obtain a valid `(body, hmac)` pair, after which the `shop-domain` header can be freely modified on replay since it is never checked against the signature.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) values in the HMAC-signed material, or otherwise cryptographically bind the tenant identity to the signature (e.g., verify the header-derived shop against a shop encoded within the signed body, or require the host application to independently confirm that `data.shop` corresponds to a shop with an active, matching webhook registration/subscription id before trusting it). At minimum, `Webhooks::Request#to_signable_string` should incorporate the shop-domain header so that `HmacValidator.validate` fails whenever any header used as an identity field is altered relative to what was originally signed.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com` and triggers any registered webhook topic (e.g., `orders/create`) for their own shop, capturing the raw POST body `B` and the `X-Shopify-Hmac-SHA256` header value `H` sent by Shopify (computed as `HMAC-SHA256(api_secret_key, B)`).
2. Attacker replays the exact same body `B` and header `H` to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` from `attacker-shop.myshopify.com` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (== `B`) and it matches `H`, so validation succeeds: [3](#0-2) 
4. The registered handler is invoked with `WebhookMetadata.shop == "victim-shop.myshopify.com"` even though the payload body content is entirely attacker-controlled from their own shop's webhook delivery, demonstrating the shop identity is not bound to the HMAC.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
