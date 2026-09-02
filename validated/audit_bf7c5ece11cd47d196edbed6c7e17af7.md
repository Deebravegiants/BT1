This confirms the vulnerability class. The `ShopifyAPI::Webhooks::Request#hmac` signable string is derived only from `@raw_body`, while `shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header without being part of the HMAC computation or independently validated against `ShopValidator`.Confirmed: `ShopifyAPI::Webhooks::Request#shop` is read straight from an HTTP header, never passed through `ShopValidator` and never included in `to_signable_string`, so the HMAC (computed only over `@raw_body`) can never detect tampering with it.### Title
Webhook shop identity can be spoofed because `shop-domain` header is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` trusts `request.shop`, which is read verbatim from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, while the HMAC that "authenticates" the webhook only covers the raw request body. This breaks the intended binding `authenticated_shop == shop_delivered_to_handler`, letting anyone who can produce one valid `(body, hmac)` pair for the app (e.g. by installing the app on their own store and capturing a legitimate webhook delivery) replay that same body/HMAC to the app's webhook endpoint with an arbitrary `shop-domain` header value, causing `WebhookMetadata#shop` to report a victim shop while carrying attacker-chosen body content.

### Finding Description
`ShopifyAPI::Webhooks::Request` is constructed straight from raw HTTP input: [1](#0-0) 
and the HMAC signable string used for verification is only the raw body: [2](#0-1) 

`Utils::HmacValidator.validate` computes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it to the `hmac` field of the request — it never inputs `shop`: [3](#0-2) 

`Registry.process` validates only this body-only HMAC and then hands `request.shop` (the unauthenticated header value) straight to the registered handler as `WebhookMetadata#shop`: [4](#0-3) [5](#0-4) 

No call to `Utils::ShopValidator` (used elsewhere in the gem, e.g. `lib/shopify_api/utils/shop_validator.rb`, to sanitize/authenticate shop domains) is made on `request.shop`, and the header is never included in `to_signable_string`. The documented handler contract explicitly tells integrators to trust `data.shop` as "The shop domain of the webhook": [6](#0-5) 

Because the app's `api_secret_key`/client secret is shared across every merchant that installs the app, any unprivileged internet user who installs the app on their own store will legitimately receive real `(body, hmac)` pairs signed with that same shared secret. They can then replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting a victim's `shop-domain` header — the HMAC check still passes because it never examined the header, and `Registry.process` will invoke the handler with `data.shop == "victim-shop.myshopify.com"` and attacker-controlled `data.body`.

### Impact Explanation
This breaks the identity binding `shop_authenticated_by_hmac == shop_delivered_to_handler`, allowing cross-tenant data injection: a handler that looks up a `Session`/tenant record by `data.shop` (exactly as the gem's own documentation recommends, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) will process attacker-supplied webhook content under a victim merchant's identity. Depending on the topic (e.g. `customers/data_request`, `shop/redact`, `orders/*`), this can cause the host application to mutate, delete, or leak another tenant's data based on forged events — a cross-tenant boundary violation.

### Likelihood Explanation
Exploitation requires only: (1) the attacker be able to install the target app on their own Shopify store (a low bar for any public app), which yields at least one legitimate `(raw_body, hmac)` pair signed with the app's shared secret, and (2) the ability to send an arbitrary HTTP POST to the app's public webhook callback endpoint with a forged `shop-domain` header. No access to `api_secret_key`, tokens, or the victim's credentials is required.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or independently authenticate `request.shop` against the set of shops actually installed for the app (e.g., verify a matching active `Session` exists) before constructing `WebhookMetadata`. At minimum, run `request.shop` through `Utils::ShopValidator.sanitize!` and cross-check it against expected/known shops, and document to integrators that `data.shop` is not itself cryptographically authenticated.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers a webhook subscription (e.g. `orders/create`).
2. Shopify delivers a legitimate webhook: `raw_body = B`, header `shopify-hmac-sha256 = HMAC(secret, B)`, header `shopify-shop-domain = attacker-shop.myshopify.com`.
3. Attacker replays this exact `raw_body` and `hmac` header to the app's webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes `HMAC(secret, B)` (from `to_signable_string`, which ignores headers) and it matches, so `Registry.process` proceeds:
   `lib/shopify_api/webhooks/registry.rb:190` passes; `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` is passed to the app's handler, which treats attacker-controlled body `B` as legitimate data for the victim shop.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
