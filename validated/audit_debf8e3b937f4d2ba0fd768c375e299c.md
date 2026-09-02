# Title
Webhook HMAC Signature Does Not Bind `shop`, `topic`, or `webhook_id`, Enabling Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` fields that are handed to the application's webhook handler as trusted, shop-identifying metadata are read directly from unauthenticated HTTP headers and are never covered by the signature. Because the app's `client_secret` (`api_secret_key`) is shared across every shop that installs the app, any merchant who legitimately installs the app can capture one of their own genuinely-signed webhook deliveries and replay the identical `raw_body`/HMAC pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and `topic`/`webhook-id`) headers to impersonate a victim shop. The signature check still passes because it only validates the body, not the tenant-identifying headers.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are pulled straight from headers with no cryptographic binding to that body: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string`, i.e. the body: [3](#0-2) 

`Registry.process` performs the HMAC check, then immediately forwards the unauthenticated header-derived `shop`, `topic`, and `webhook_id` values to the app's handler as trusted metadata identifying the tenant: [4](#0-3) 

Equality the code should enforce but does not: `hmac_valid(raw_body) == true` should imply `shop header == shop that Shopify actually generated this signature for`. In reality, `hmac_valid(raw_body)` only proves the body was signed with *the app's* `api_secret_key` at some point — a secret shared by every shop that has installed the app — not that the accompanying `shop`/`topic`/`webhook_id` headers were the ones Shopify attached to that specific signed body. Any of the app's own merchants can therefore reuse a signature that was valid for their own webhook to make the app believe an arbitrary body originated from a different shop.

### Impact Explanation
This breaks the tenant-isolation guarantee that `WebhookMetadata#shop` is trustworthy. Host applications built on this gem's documented webhook API (per `docs/usage/webhooks.md`) are expected to key persistence/side effects off `data.shop`, e.g., "update shop X's order/inventory record using this body." An attacker who has legitimately installed the app on their own store can forge a webhook that the app processes as belonging to a victim shop, injecting attacker-controlled body content attributed to that victim tenant. This is a cross-tenant integrity/confidentiality violation reachable by any unprivileged internet user who is (or becomes) an installer of the target app — no leaked credentials or privileged access to the victim account required.

### Likelihood Explanation
Requires only: (1) installing the target Shopify app on any shop (self-service, unprivileged), which yields genuine webhook deliveries signed with the app's shared `api_secret_key`; and (2) replaying the captured `raw_body` + HMAC to the app's public webhook endpoint with modified `shop-domain`/`topic`/`webhook-id` headers. No secret material needs to be known or brute-forced by the attacker.

### Recommendation
Bind the tenant-identifying fields into the authenticated payload, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the signed body — e.g., verify the `shop` header against an out-of-band record of which shop the app expects to be receiving webhooks for (offline session store keyed by shop), reject deliveries whose `shop` header does not match a previously-established session for this installation, or require that these fields be incorporated into the value that is HMAC-verified rather than trusted as raw headers.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook topic the app registers for (e.g. `orders/create`).
2. Capture the resulting HTTP request: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H` is valid because `OpenSSL::HMAC.hexdigest(sha256, api_secret_key, B) == H` (per `Utils::HmacValidator.validate_signature`, [3](#0-2) ).
3. Replay the identical body `B` and header `H` to the same app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com` (and, if desired, a different `x-shopify-webhook-id`/`x-shopify-topic`).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H` ( [5](#0-4) ). The handler is then invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` ( [6](#0-5) ), causing the app to process attacker-supplied content as though it came from the victim shop.

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
