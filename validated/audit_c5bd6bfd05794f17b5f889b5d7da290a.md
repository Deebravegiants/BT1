### Title
Webhook shop/topic/webhook_id identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` implements `VerifiableQuery` such that only the raw request body is included in the HMAC-signed material, while the `shop`, `topic`, and `webhook_id` values — which are used by `Registry.process` to route the webhook and identify the tenant — are read from HTTP headers that are excluded from the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `Request#shop`, `#topic`, and `#webhook_id` are pulled straight from headers, which are never part of the signable string: [2](#0-1) [3](#0-2) 

`Utils::HmacValidator.validate` only re-computes the HMAC over `verifiable_query.to_signable_string` (i.e. the body) and compares it to the `hmac` header value — it never binds the `shop`/`topic`/`webhook_id` headers into that computation: [4](#0-3) 

`Registry.process` trusts these unauthenticated header values to build `WebhookMetadata`, which is the tenant/topic identity handed to the consuming app's handler: [5](#0-4) [6](#0-5) 

The identity binding that should hold is: `shop header used to route the webhook == shop cryptographically bound by the HMAC`. In this implementation that equality does not hold — the HMAC only proves "this body byte-sequence was produced with the shared secret", not "this body was produced by shop X" or "this body corresponds to topic Y". Any actor who legitimately receives one webhook delivery for their own shop (which any Shopify app developer/merchant can trigger, e.g. via `app/uninstalled` or any topic with a low/empty-information body such as `{}`) obtains a valid `(raw_body, hmac)` pair. They can then replay that exact body+HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, and `X-Shopify-Webhook-Id` headers to claim it came from a different (victim) shop or topic. `HmacValidator.validate` will still pass because it only checks the body bytes against the signature, and `Registry.process` will hand the handler a `WebhookMetadata` with the forged `shop`/`topic`, causing the host application to act on data for a shop it never actually came from.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: an attacker with access to a single legitimately-signed webhook body can impersonate another shop or another topic without ever possessing the app's `client_secret` or any shop's access token, this qualifies as cross-tenant access.

### Likelihood Explanation
Any developer/merchant who can install the app (even a single low-privilege installation on a shop they control) can capture a valid `(body, hmac)` pair for any registered topic and use it to forge deliveries against arbitrary `shop`/`topic`/`webhook_id` header values — the exploit requires no secret material and no more privilege than what "unprivileged internet user" scope allows for this analysis, since header spoofing to the app's own public webhook endpoint is fully attacker-controlled.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string (or otherwise cryptographically bind them, mirroring how the OAuth `HmacValidator` binds all relevant query parameters) so that `HmacValidator.validate` fails if any of these header-derived identity fields are altered relative to what Shopify actually signed.

### Proof of Concept
1. App registers a handler for topic `some/topic`.
2. Attacker triggers (or otherwise obtains) a legitimate webhook delivery to their own shop, e.g. body `"{}"` with a valid `x-shopify-hmac-sha256` computed by Shopify using the app's shared secret over that body — this is a normal `POST` the attacker can capture with a local proxy or logging middleware since it is delivered to *their own* endpoint.
3. Attacker resends the same body and same `hmac` header to the app's webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or a different `x-shopify-topic`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) recomputes HMAC over the unchanged body and matches successfully.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: forged_topic, ...)`, and the host application processes data believing it originated from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
