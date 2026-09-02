This confirms the vulnerability. The documented and intended API flow (`docs/usage/webhooks.md`) explicitly tells app developers to trust `data.shop` as "The shop domain of the webhook" for tenant-scoped processing, while the HMAC computation (`Utils::HmacValidator.validate`) only signs `to_signable_string`, which returns `@raw_body` alone — the `shop-domain` header is never part of the signed material.

### Title
Webhook HMAC only covers the request body, not the `shop-domain` header, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, and `ShopifyAPI::Webhooks::Registry.process` validates that body-only HMAC before dispatching to the app's handler with `request.shop` taken from an unauthenticated header. Any attacker who can obtain one valid `(raw_body, hmac)` pair signed by the app's shared `api_secret_key` — for example a webhook Shopify sends to their own shop, since the secret is per-app, not per-shop — can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting a different `shop-domain` header for a victim shop. The HMAC still validates because it never covered the `shop` value, so the app's handler processes the payload as if it belongs to the victim shop.

### Finding Description
The identity binding that should hold is: `hmac == HMAC(secret, shop || body)`, i.e., the tenant identifier should be part of what's authenticated. Instead the code implements `hmac == HMAC(secret, body)`: [1](#0-0) 

`Registry.process` only checks this body-only HMAC before calling the handler with the unauthenticated `shop` header: [2](#0-1) 

`HmacValidator.validate` confirms the signable string is the only material verified against the shared `api_secret_key`: [3](#0-2) 

Because `api_secret_key` is scoped to the *app*, not to an individual shop, every shop that has the app installed receives webhooks signed with the same secret. An attacker who installs the app on their own (attacker-controlled) shop can legitimately receive real Shopify webhooks with valid `(raw_body, hmac)` pairs for that shop, then replay the identical body and HMAC to the app's public webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header changed to a victim shop's domain. The HMAC validation passes because the header was never signed, and the app's `WebhookHandler#handle` is invoked with `data.shop` set to the victim's domain per the documented contract: [4](#0-3) 

Any host application following this documented pattern to scope stored/updated data by `data.shop` will attribute attacker-supplied webhook content to the victim tenant.

### Impact Explanation
This breaks the shop-authenticated-vs-shop-acted-upon binding, enabling cross-tenant data injection/corruption: an attacker can make the app process falsified webhook data under another merchant's shop identity, all while passing the gem's own signature check. This matches the "Critical — cross-tenant access" impact category.

### Likelihood Explanation
Exploitability requires only: (1) an attacker-controlled shop with the app installed (trivial for any public app), enabling capture of a genuine `(raw_body, hmac)` pair, and (2) the ability to POST to the app's public webhook receiver endpoint (webhook endpoints are internet-facing by design). No access token, `api_secret_key`, or privileged account is required — only unprivileged internet/merchant access.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values as part of the signable string used for HMAC computation, or otherwise cryptographically bind the shop identity to the signed payload before it's trusted for tenant-scoped processing, so a valid HMAC for one shop cannot be replayed under a different shop's identity.

### Proof of Concept
1. App developer follows `docs/usage/webhooks.md` and implements a handler that stores/acts on `data.body` keyed by `data.shop`.
2. Attacker installs the app on shop `attacker.myshopify.com`, triggers an event (e.g., `orders/create`), and captures the resulting POST — raw body `B` and header `x-shopify-hmac-sha256: H` — sent to the app's public webhook URL (this is a real, currently-valid Shopify signature for body `B`).
3. Attacker sends their own POST to the same webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` in [5](#0-4)  succeeds because it only checks `body` against the shared secret.
5. `Registry.process` in [6](#0-5)  calls the handler with `shop: "victim.myshopify.com"` and the attacker's body content, causing the host app to act on victim data with attacker-controlled content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
