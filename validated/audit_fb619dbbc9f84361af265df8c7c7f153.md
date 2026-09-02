### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies its HMAC over the raw request body only, but the `shop` (and `topic`, `webhook_id`, `api_version`) values that are later trusted by the host application are read from HTTP headers that are never included in the signed content. Because a single app-level `client_secret` is used to sign webhooks for *every* shop that installs the app, any shop owner who receives a legitimately-signed webhook for their own store can replay that exact body+HMAC pair while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header for a different, victim shop domain. The signature will still validate, and `ShopifyAPI::Webhooks::Registry.process` will hand the attacker-chosen `shop` value straight to the app's webhook handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all read independently from headers that are not part of the signable string: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. it only binds the *body* to the signature, never the headers: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (from the unsigned header) to build the `WebhookMetadata` passed to the developer's handler: [4](#0-3) 

The identity binding that should hold is: `hmac-verified(shop) == shop passed to handler`. In reality the equality that holds is only `hmac-verified(raw_body) == raw_body`; `shop` is parsed from bytes that were never authenticated. Since Shopify signs webhooks with the app's single `client_secret` (the same secret is used for all shops of that app), a user who controls one shop (and thus receives real, validly-signed webhooks for that shop) can capture a `(body, hmac)` pair and resend it to the app's webhook endpoint with the `shop-domain` header swapped to any other shop that installed the same app. `HmacValidator.validate` still returns `true` because it never inspected the header, and `Registry.process` forwards the attacker-chosen shop straight into `WebhookMetadata#shop`, which per the documented usage (`docs/usage/webhooks.md`) is exactly the field host apps use to scope stored data to a tenant: [5](#0-4) [6](#0-5) 

### Impact Explanation
This is a cross-tenant identity-spoofing vector inside a shared-secret multi-tenant model: an attacker who is a legitimate (even free/trial) installer of the app for their own shop can forge webhook events “for” any other shop using the same app, because the gem's HMAC validation never binds the body to the header-derived shop. Any host application that relies on `WebhookMetadata#shop` (as documented) to key writes/updates without independently re-validating shop ownership will process attacker-controlled data under another merchant's identity — i.e., cross-tenant data injection.

### Likelihood Explanation
Likelihood is meaningful but bounded: the attacker must be an installer of the target app (to obtain one validly-signed body/HMAC), and the victim must also have the app installed and be a webhook topic the attacker also subscribes to (so the JSON body shape matches expected fields, or the attacker controls a body that will be misinterpreted, e.g. `shop/redact`, `orders/create` with attacker-controlled body content for their own shop, replayed as if it came from the victim). This is not a trivial unauthenticated pre-auth exploit, but it requires no secret material beyond normal app installation, matching an "unprivileged internet user" analog.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook_id`) header value in `to_signable_string`, or otherwise fold header-derived identity fields into the HMAC computation, so the signature binds the tenant identity to the payload rather than the payload alone.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), receiving a POST with body `B` and header `x-shopify-hmac-sha256: H` where `H = HMAC(client_secret, B)`.
2. Attacker replays the exact same request to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, B)` and matches `H` — validation succeeds because the header was never part of the signed data: [7](#0-6) 
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)` and (per documented usage) persists/acts on `B` as if it came from the victim shop.

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
