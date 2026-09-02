This confirms the analog: the docs (line 125) explicitly state `Registry.process` "will verify the request did indeed come from Shopify" — but the verification only covers the raw body, not the `shop` (and `topic`/`webhook_id`) headers that the host app is told to trust as tenant identity for the webhook (line 14: "`shop`, `String` - The shop domain of the webhook").### Title
Webhook `shop` (tenant identity) header is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies the authenticity of an incoming webhook by validating only the HMAC over the raw request body, while the `shop` identity that the host application uses to attribute the event to a tenant is read from an HTTP header that is completely outside the signed data. This breaks the identity binding `shop_verified_by_HMAC == shop_acted_on`, allowing a request whose body signature is valid (i.e., a genuine webhook payload that the attacker received for their own, attacker-controlled shop) to be replayed with a modified `shop-domain`/`x-shopify-shop-domain` header and be accepted as if it originated from a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all pulled from HTTP headers, none of which are part of the signable string: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` and then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` passed to the app's handler, without any additional binding check between the verified body and the unverified headers: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the raw body for webhooks) and the app's `api_secret_key`: [4](#0-3) 

The gem's own documentation instructs developers to trust `data.shop` as "The shop domain of the webhook" and states that `Registry.process` "will verify the request did indeed come from Shopify," implying the whole request (including its claimed shop) is authenticated — which is not the case: [5](#0-4) [6](#0-5) 

This is the identity-binding failure pattern called out in scope: "a field acted on but not covered by the HMAC." The field acted on downstream (tenant/shop attribution for business logic, job enqueuing, per-tenant data writes) is the `shop-domain` header, while the field actually covered by the HMAC is only the JSON body bytes.

### Impact Explanation
Any actor who can obtain one legitimately signed webhook body for their own shop (trivial — any merchant/developer installing the app receives real signed webhooks for their own store) can replay that exact body while substituting the `Shopify-Shop-Domain` (or `X-Shopify-Shop-Domain`) header with a victim shop's domain. Because `HmacValidator.validate` never inspects headers, the forged request passes signature validation and is routed to the registered handler with `WebhookMetadata#shop` set to the victim's domain. Any host application following the documented contract (using `data.shop` to key session/access-token lookups, enqueue per-tenant jobs, or write to per-tenant records) will process attacker-controlled data as if it came from the victim's store — a cross-tenant data/action injection. This matches the "Critical - cross-tenant access" impact category, since it crosses the tenant boundary that the gem is documented to enforce via HMAC verification.

### Likelihood Explanation
High likelihood of exploitability given the documented usage pattern. An attacker only needs their own merchant/developer account (unprivileged relative to any other tenant) to obtain a validly-signed webhook body, and standard HTTP tooling to replay it with a modified header. No access token, `client_secret`, or privileged credential is required — only observation of one's own legitimately delivered webhook traffic, which any app-installing merchant can do.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) claims to the cryptographic verification instead of trusting unauthenticated headers:
- Include the shop domain (and other identity-bearing headers) in the HMAC-signed material used for webhook validation, or
- Cross-check the header-derived `shop` against an independently-authenticated source (e.g., match against the shop associated with the specific webhook subscription/session the app registered), and reject/log mismatches, or
- At minimum, document prominently that `request.shop`/`data.shop` is NOT authenticated by the HMAC check and must not be used as a sole tenant-selection key without additional verification (e.g., confirming an active, previously-established session exists for that shop before trusting webhook content tied to it).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers a webhook (e.g., `orders/create`).
2. Attacker triggers an order-create event, capturing the raw POST body and the legitimate `X-Shopify-Hmac-Sha256` header Shopify sent to the app's webhook endpoint.
3. Attacker resends this exact captured request to the app's webhook endpoint, but rewrites the `X-Shopify-Shop-Domain` header to `victim-shop.myshopify.com` (all other headers/body unchanged).
4. `ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` are computed purely from the (unchanged) body/hmac header, so `Utils::HmacValidator.validate(request)` still returns `true` per [7](#0-6)  and [8](#0-7) .
5. `Registry.process` accepts the forged request and invokes the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: attacker-controlled JSON, ...)` per [9](#0-8) , causing the host app to process attacker-supplied data under the victim tenant's identity.

Note: I could not locate the `WebhookMetadata` class definition file directly (only its reference inside `webhook_handler.rb`) due to index coverage limits; if deeper inspection of how `shop` propagates into consumer applications is needed, a full Devin session with repo access would allow confirming additional downstream usage sites, though the core signing gap is fully demonstrated from `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, and `lib/shopify_api/webhooks/registry.rb`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
