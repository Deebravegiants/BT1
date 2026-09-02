### Title
Webhook `shop` Attribution Is Not Covered By The HMAC, Allowing Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` value used to attribute the webhook to a specific merchant tenant is read from an unsigned HTTP header. Any party who can produce (or observe) one validly-signed webhook body/HMAC pair can replay it with an arbitrary `X-Shopify-Shop-Domain` header and still pass HMAC verification, letting them attribute forged/replayed webhook data to any tenant they choose.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but the `shop` accessor, which identifies the tenant the webhook is attributed to, is pulled straight from the `shop-domain` header and is never part of the signed content: [2](#0-1) 

`Registry.process` validates the HMAC over the body via `HmacValidator.validate`, and then, on success, hands `request.shop` (unauthenticated) directly to the app's handler as the tenant identifier without any additional binding check: [3](#0-2) 

`HmacValidator.validate_signature` only checks `verifiable_query.to_signable_string` (the body) against the HMAC — it never incorporates `shop`: [4](#0-3) 

The identity binding that should hold is:
`shop attributed to handler == shop that the HMAC actually authenticates`

But because `to_signable_string` excludes the header-derived `shop`, the equality collapses to:
`shop attributed to handler == <unauthenticated header value>`

This is directly analogous to the referenced report's root cause — a value that is *acted upon* (there: `pool3`/`usdm` amounts used for liquidity; here: `shop` used for tenant attribution) is not the value that is actually *verified* (there: only `usdm` balance truncation was checked; here: only the raw body is HMAC-checked).

### Impact Explanation
Any attacker who has a validly-signed webhook body+HMAC pair (e.g., from installing the target app on their own shop and triggering an event) can resend that exact body/HMAC to the app's public webhook endpoint while swapping the `X-Shopify-Shop-Domain` header to any victim shop domain. `HmacValidator.validate` still returns `true` because it never inspects the header, and `Registry.process` passes the attacker-chosen `shop` value straight to the app's `handler.handle` call as `WebhookMetadata#shop`. Any app logic that uses `data.shop` to decide which tenant's records to create, update, or delete is now cross-tenant-controllable by an unprivileged internet user who never needs the app's `client_secret`, an access token, or any privileged account — this matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high: obtaining one legitimate signed webhook (body + HMAC) is trivial for anyone who can install the app on a shop they control (or observe any webhook delivery), and the header swap requires no cryptographic effort — it exploits the fact that the header is simply never covered by `to_signable_string`.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) in the value that is HMAC-verified, or independently bind the header-derived `shop` to a value contained in and covered by the signed body/payload before it is trusted for tenant attribution. At minimum, document and enforce that `request.shop` must not be treated as authenticated unless corroborated by signed content.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook event (e.g. `orders/create`), capturing the genuine `raw_body`, `X-Shopify-Hmac-Sha256`, and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com` headers sent to the app's public webhook endpoint.
3. Attacker resends the identical POST to the same endpoint, keeping `raw_body` and `X-Shopify-Hmac-Sha256` unchanged, but replacing the header with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `hmac` and `to_signable_string` (raw body) are unchanged and thus still valid; `HmacValidator.validate` returns `true` as shown in [5](#0-4)  since only the body is checked.
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop` is now `"victim-shop.myshopify.com"`, as shown in [3](#0-2) , causing the app to process attacker-controlled webhook data under the victim tenant's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
