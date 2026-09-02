## Title
Webhook `shop` (and `topic`/`webhook-id`) identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once `Utils::HmacValidator.validate` succeeds, and then forwards `request.shop`, `request.topic`, and `request.webhook_id` to the app's handler as trusted identity fields. However, the HMAC signature only covers the raw JSON body, not these header-derived fields, so an attacker who can produce a valid HMAC for a given body (i.e., anyone who has received one legitimate webhook payload for any shop on the app) can replay that exact body with a forged `shopify-shop-domain` header pointing at a different shop, and the gem will still report it as a validated, authentic webhook for that other shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` is defined as: [1](#0-0) 

Only `@raw_body` is signed. The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all read directly from headers that are never part of the signable string: [2](#0-1) 

`Registry.process` uses `Utils::HmacValidator.validate(request)` as the sole authenticity gate, then immediately constructs `WebhookMetadata` from the unauthenticated header fields and calls the app's handler with them: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (i.e., only the body for webhooks) and the shared `api_secret_key`: [4](#0-3) 

Because a single `api_secret_key`/`old_api_secret_key` pair is shared across every shop that has the app installed, any tenant that legitimately receives one authentic webhook (with a valid HMAC for a given raw body) also learns a valid `(body, hmac)` pair signed with the app's secret. That pair remains valid regardless of which `shopify-shop-domain` header accompanies it, since the header is not part of the signed content. The identity binding the gem implicitly claims to enforce — "HMAC-valid request" ⇔ "request truly originated for shop X" — does not hold; it only proves "this body was signed by the app's secret," decoupled from the shop-domain claim.

The library's own documentation frames `Registry.process` as verifying that "the request did indeed come from Shopify" and describes `data.shop` as simply "the shop domain of the webhook," with no caveat that this field is unauthenticated: [5](#0-4) [6](#0-5) 

This mirrors the report's bug class: a field (`shop`) that is acted upon and trusted by the identity/authorization logic but is not covered by the cryptographic check that is supposed to establish trust.

### Impact Explanation
Any tenant of a multi-tenant app that receives at least one legitimate webhook delivery (a normal, unprivileged occurrence for any merchant that installs the app) can capture a valid `(raw_body, hmac)` pair and replay it against the app's webhook endpoint with an arbitrary `shopify-shop-domain` header. Because `Registry.process` passes the (forged) `shop` value straight through to the handler as an already-"validated" identity, any app that uses `data.shop` to select the tenant context — e.g., to look up a session/access token, scope a background job, or write data — will act on behalf of a different shop than the one that actually sent the request. This is a cross-tenant identity binding break traceable directly to this gem's webhook verification code, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only capturing one legitimate webhook body+HMAC pair from any shop where the attacker has legitimate (even unprivileged) app access, and the ability to send an HTTP POST to the app's public webhook endpoint with a custom `shopify-shop-domain` header — both are within reach of an unprivileged internet user/tenant, with no need for `api_secret_key`, tokens, or TLS interception.

### Recommendation
Bind the identity-bearing headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) into the signed material — or otherwise independently authenticate the shop domain (e.g., cross-check it against a known/installed shop record before trusting it), rather than relying solely on a body-only HMAC and unauthenticated headers, in `lib/shopify_api/webhooks/request.rb` and `lib/shopify_api/webhooks/registry.rb`.

### Proof of Concept
1. App is installed on Shop A and Shop B, sharing one `api_secret_key`.
2. Shop A (attacker-controlled/observed) legitimately receives a webhook: raw body `B` with header `x-shopify-shop-domain: shop-a.myshopify.com` and a valid `x-shopify-hmac-sha256` computed over `B`.
3. Attacker replays the same body `B` and the same HMAC header, but sets `x-shopify-shop-domain: shop-b.myshopify.com`, to the app's webhook endpoint.
4. `Utils::HmacValidator.validate` succeeds because it only checks `B` against the secret (`lib/shopify_api/utils/hmac_validator.rb:12-31`); `Registry.process` proceeds and calls the handler with `data.shop == "shop-b.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:188-200`), even though the request never originated from Shop B.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
