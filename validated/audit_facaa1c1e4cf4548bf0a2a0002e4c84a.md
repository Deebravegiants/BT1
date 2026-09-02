## Title
Webhook shop/topic identity spoofing via HMAC that only covers the raw body — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic for a given `shop` and `topic` as soon as `Utils::HmacValidator.validate(request)` succeeds. However, the HMAC signature computed by this gem only covers the raw request body — the `shop-domain` and `topic` header values that the gem uses to route and attribute the webhook are never part of the signed content. This breaks the intended binding `HMAC-authenticated bytes == (shop, topic, body)` down to just `HMAC-authenticated bytes == body`.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`HmacValidator.validate_signature` computes and compares the HMAC exclusively over that signable string: [2](#0-1) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from unsigned HTTP headers with no cryptographic binding to the body or to each other: [3](#0-2) 

`Registry.process` only checks the HMAC and then dispatches the handler using these unsigned `shop`/`topic` values, treating them as trustworthy tenant/routing identifiers: [4](#0-3) 

Because a single app-wide `api_secret_key` (`Context.api_secret_key`) is used to validate webhooks for *every* shop that has installed the app, any unprivileged merchant who installs the app can capture a genuinely-HMAC-valid webhook delivery for their own store, then replay it to the app's webhook endpoint after modifying only the unsigned `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header. The HMAC check still passes because it only re-validates the untouched body, so `Registry.process` will invoke the topic handler believing the data belongs to the attacker-chosen `shop` value — this is directly analogous to the reported bug class: an identifier the application acts on (`shop`) is not covered by the integrity check (`HMAC`) that gates trust in the request.

### Impact Explanation
This crosses the "cross-tenant access" Critical bucket: an app built on this gem that uses the (unsigned) `shop` value from `WebhookMetadata` to select a tenant record, write data, or trigger tenant-scoped side effects can be tricked into attributing attacker-controlled-but-HMAC-valid webhook payloads to a victim merchant's shop, since the gem provides no protection against shop-domain spoofing beyond the body-only HMAC.

### Likelihood Explanation
Any user who can install the app on their own store (a normal, unprivileged flow) obtains real webhook deliveries with valid HMACs. Forging the `shop-domain`/`topic` headers on a replayed HTTP request requires no secret material, only network access to the app's public webhook endpoint — no `api_secret_key`, access token, or privileged account is needed.

### Recommendation
Bind `shop` (and ideally `topic`) into the value that is HMAC-verified, or otherwise cross-check the header-derived `shop` against a shop the app has independently confirmed to have installed and to be expecting that `webhook_id`, before trusting `request.shop` in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`; Shopify delivers a legitimate webhook with a valid `X-Shopify-Hmac-Sha256` header computed over the JSON body using the app's shared `api_secret_key`.
2. Attacker captures this request and replays it to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (and, if desired, `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — this passes because it only checks the unmodified body against the (still-valid) HMAC.
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the app to process attacker-supplied data as if it came from the victim shop.

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
