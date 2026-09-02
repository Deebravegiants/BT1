This confirms the vulnerability path. The `Utils::VerifiableQuery` interface only requires `hmac` and `to_signable_string`, and `Webhooks::Request#to_signable_string` returns solely `@raw_body` [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` values are all pulled straight from HTTP headers [2](#0-1) , and `Registry.process` trusts these header-derived values to build `WebhookMetadata` for the handler after only checking the body-only HMAC [3](#0-2) .

### Title
Webhook `shop`/`topic` identity fields are not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts the `shop-domain`, `topic`, and `webhook_id` values taken from unauthenticated HTTP headers to build the `WebhookMetadata` passed to the app's handler.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` and defines `to_signable_string` to return only `@raw_body` [1](#0-0) . `HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (the raw body) using the app's shared `api_secret_key` [4](#0-3) . Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from the `shopify-*`/`x-shopify-*` HTTP headers with no cryptographic binding to the HMAC [2](#0-1) .

`Registry.process` validates the HMAC and then immediately constructs `WebhookMetadata` using `request.shop` and `request.topic` taken from these unauthenticated headers, dispatching them to the registered handler as if they were verified [3](#0-2) .

Since the same `api_secret_key` is shared by the app across all of its installed shops, any merchant who has installed the app can receive a legitimate webhook delivery from Shopify to their own store, capture the raw body and its valid `hmac-sha256` header, and then replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` header (and/or `topic` header) pointing at a different, victim shop. The equality the app implicitly relies on — "shop header value == shop that produced this HMAC-authenticated body" — does not actually hold, because the header is never part of the signed content.

### Impact Explanation
This breaks the tenant-identity binding: `WebhookMetadata.shop` is treated by host applications as an authenticated tenant identifier used to look up sessions/records and persist incoming webhook data, but it is fully attacker-controlled while riding on a validly-signed body. This allows a malicious merchant to inject or spoof webhook data attributed to a victim shop, causing cross-tenant data confusion in any host application that trusts `WebhookMetadata.shop`/`topic` after `Registry.process` succeeds.

### Likelihood Explanation
Any unprivileged party who can install the app on their own store (a normal customer/merchant capability) can capture a real webhook to obtain a body+HMAC pair signed with the app's `api_secret_key`, then replay it with a forged `shop-domain` header at the app's public webhook receiving endpoint. No access token, `client_secret`, or privileged access is required — only normal app installation and observation of one's own webhook traffic.

### Recommendation
Bind the `shop`, `topic`, and `webhook_id` fields into the HMAC-signed content (or otherwise cryptographically verify `shop`/`topic` against a value independently known to the app, e.g., resolved from a stored session/access-token record) rather than trusting header values that sit outside `to_signable_string`. At minimum, `Registry.process` should cross-check that the `shop` header corresponds to a shop with an active session/installation before dispatching to handlers.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook from Shopify, e.g. body `{"id":1}` with header `x-shopify-hmac-sha256: <valid-hmac-of-body>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays the identical raw body and `hmac-sha256` header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` succeeds because it only checks the raw body against the shared secret [5](#0-4) .
4. `Registry.process` builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and dispatches to the handler [6](#0-5) , causing the host app to process attacker-supplied data as if it originated from the victim's shop.

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
