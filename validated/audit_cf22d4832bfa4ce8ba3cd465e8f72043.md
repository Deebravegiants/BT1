This confirms the finding: the documentation explicitly claims `Registry.process` "will verify the request did indeed come from Shopify," but the actual implementation only verifies HMAC integrity over the raw body, while `topic`, `shop-domain`, `api-version`, and `webhook-id` headers pass through unauthenticated into `WebhookMetadata`.

### Title
Webhook `shop`, `topic`, and `webhook-id` Identity Fields Are Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body [1](#0-0) . However, the identity-carrying fields that the handler receives and trusts — `shop`, `topic`, `api_version`, and `webhook_id` — are parsed straight from HTTP headers and are never included in the signed bytes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

`HmacValidator.validate` computes the HMAC exclusively over that signable string (the body) and compares it against the `hmac` header: [3](#0-2) 

Meanwhile, `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated headers: [4](#0-3) 

`Registry.process` passes these unauthenticated fields straight into `WebhookMetadata`, which is handed to the app's handler as the trusted tenant/topic identity: [1](#0-0) 

The identity binding broken is: **`hmac` verifies `raw_body` bytes ≠ `shop`/`topic`/`webhook_id` bytes that the handler actually acts on.** Any party that possesses one valid `(raw_body, hmac)` pair for their own tenant — i.e., any merchant who has installed the app and receives real webhooks — can replay that exact body/HMAC pair while substituting the `shop-domain` (and/or `topic`/`webhook-id`) header for any other shop. Because the HMAC never covers those headers, `HmacValidator.validate` still returns `true`, and `Registry.process` invokes the handler with `WebhookMetadata#shop` set to the spoofed victim shop.

The library's own documentation asserts a authentication guarantee broader than what is implemented: "This will verify the request did indeed come from Shopify" [5](#0-4) , when in fact only the body's authenticity is verified, not the sender-asserted shop/topic identity.

### Impact Explanation
Applications built on this gem commonly use `WebhookMetadata#shop` as the tenant key to look up a stored session/access token and perform authenticated follow-up actions (e.g., "on `orders/create` for shop X, call the Admin API using shop X's stored token"). Because a malicious existing merchant can forge the `shop` field for a webhook payload attributed to a different shop while keeping a body/HMAC pair that still validates, the merchant can cause the host application to process attacker-controlled webhook data under another tenant's identity — a cross-tenant integrity/access violation with the app's own credentials for the spoofed tenant.

### Likelihood Explanation
Any merchant who legitimately installs the app on their own store immediately obtains one or more valid `(raw_body, hmac)` pairs (their own real webhook deliveries), which is the only prerequisite. No knowledge of `api_secret_key` is required — the merchant simply resends a previously-received, still-valid webhook HTTP request with the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header changed to the victim's domain. The exploit primitive is a straightforward unauthenticated header substitution requiring only internet access to the app's webhook endpoint.

### Recommendation
Bind the `shop`, `topic`, and `webhook_id` header values into the signed material, or independently verify `shop` against the caller's registered/expected tenant before constructing `WebhookMetadata`. At minimum, document that `shop`/`topic`/`webhook_id` are unauthenticated and must not be used as a sole tenant-lookup key without corroboration (e.g., cross-checking against the currently active session for that shop, or validating shop domain format/allowlist plus rate-limiting duplicate `webhook_id`s per shop).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a real webhook (e.g., `orders/create`), capturing the exact raw body and its `X-Shopify-Hmac-Sha256` header value delivered by Shopify.
2. Attacker crafts an HTTP POST to the app's webhook endpoint reusing that identical raw body and HMAC header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally alters `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. `ShopifyAPI::Webhooks::Request.new` parses `shop` from the forged header [6](#0-5) .
4. `HmacValidator.validate` recomputes the HMAC over `raw_body` only and it matches, since the body is unchanged [7](#0-6) .
5. `Registry.process` invokes the registered handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though Shopify never sent this data for that shop [1](#0-0) .

### Citations

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

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
