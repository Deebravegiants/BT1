## Finding

### Title
Webhook HMAC verification does not bind the signature to the `shop-domain` header, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic once `Utils::HmacValidator.validate(request)` succeeds, and the docs explicitly promise this call "will verify the request did indeed come from Shopify." [1](#0-0)  In reality, the HMAC only signs the raw request body — the `shop-domain` header used to attribute the event to a tenant is never part of the signed material.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`, while `#shop` is read straight from the (attacker-controllable) `x-shopify-shop-domain`/`shopify-shop-domain` header, entirely independent of the signature: [2](#0-1) 

`HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` (i.e. the body only) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` gates entirely on this body-only check, then constructs `WebhookMetadata` using the unauthenticated `request.shop`, which is handed to the app's handler as the tenant identity: [4](#0-3) 

The identity binding the code implicitly assumes is: `shop that produced the signed bytes == shop attributed to WebhookMetadata`. Nothing enforces this equality — the signing secret (`Context.api_secret_key`, plus optionally `old_api_secret_key`) is the **same app-level secret for every shop that installed the app** [5](#0-4) , not a per-shop secret. So any merchant who has legitimately installed the app can:
1. Capture a real webhook delivered to their own shop (a valid `raw_body` + `hmac` pair, since it's signed with the app's shared secret).
2. Replay that exact `raw_body`/`hmac` pair to the app's public webhook endpoint, substituting the `x-shopify-shop-domain` header with a victim shop's domain that also uses the app.
3. `HmacValidator.validate` still succeeds (it never looked at the shop header), so `Registry.process` invokes the handler with `WebhookMetadata.new(..., shop: "<victim-shop>.myshopify.com", body: attacker_body)`.

The app's handler code (built entirely on top of `data.shop` per the documented contract [6](#0-5) ) has no way to distinguish this from a genuine webhook for the victim shop.

### Impact Explanation
This breaks tenant isolation (cross-tenant access/injection): an attacker-controlled shop can inject arbitrary, attacker-chosen webhook payloads (e.g. `orders/create`, `app/uninstalled`, GDPR `customers/redact`) that the host application will process as if they originated from a different, victim shop, purely because the gem's "verified" guarantee does not actually bind the signature to the shop identity. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any user who can install the app on their own store (a standard, unprivileged onboarding flow for public/multi-tenant Shopify apps) can obtain a valid `raw_body`/`hmac` pair and replay it against the shared, internet-reachable webhook endpoint with a forged shop header — no access token, `client_secret`, or privileged access is required.

### Recommendation
Bind the shop identity into the verified material, e.g. include the `shop-domain` (and ideally `webhook-id`/`api-version`) header value in the string that is HMAC-verified, or independently confirm that the `shop` on the request corresponds to a shop with an active session/registration for that specific webhook `topic`/`webhook_id` before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a legitimate `orders/create` webhook delivery with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(app_secret, B)`).
2. Attacker crafts their own `B'` (e.g. a fake order or an `app/uninstalled` body) if they can get any signed body from Shopify — or more directly, simply resends captured `(B, H)` unmodified but swaps only the header:
   `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
3. POST to the app's public webhook endpoint (`ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {... "x-shopify-shop-domain" => "victim-shop.myshopify.com", "x-shopify-hmac-sha256" => H ...})`).
4. `HmacValidator.validate` returns `true` (only `B` and `H` are checked); `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"`, `body: parsed(B)` — data the attacker fully controls being attributed to a shop the attacker does not own.

### Citations

**File:** docs/usage/webhooks.md (L12-18)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```

**File:** docs/usage/webhooks.md (L123-132)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
