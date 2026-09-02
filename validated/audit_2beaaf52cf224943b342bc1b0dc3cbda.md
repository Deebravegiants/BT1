### Title
Webhook shop identity is not bound by the HMAC signature, enabling cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verification performed in `HmacValidator.validate` proves nothing about the `shop`, `topic`, or `webhook_id` values that the library extracts from HTTP headers and hands to the app's handler. This breaks the intended identity binding: `HMAC_valid(body) == true` is treated as equivalent to `request.shop == authenticated_shop`, but the two are independent.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

Only `@raw_body` is fed into the HMAC computation. Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from HTTP headers, which are never covered by the signature: [2](#0-1) 

`Registry.process` verifies only the body-based HMAC and then trusts `request.shop`/`request.topic` unconditionally when building the data passed to the app's handler: [3](#0-2) 

Because the shared secret (`Context.api_secret_key`) is the **app's** secret and is identical for every merchant/shop that installs the app (see `HmacValidator.validate`, which signs with `Context.api_secret_key`): [4](#0-3) 

any unprivileged party who has legitimately installed the app on a shop they control can trigger real Shopify webhook deliveries and obtain body+HMAC pairs that are valid under the app's shared secret. Since the `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) headers are not part of the signed material, that attacker can replay the exact `raw_body`/HMAC pair to the app's public webhook endpoint while substituting a different shop's domain in the `X-Shopify-Shop-Domain` header. `Registry.process` will accept the HMAC (it only checks the body) and dispatch `WebhookMetadata.new(shop: request.shop, ...)` to the app's handler with the attacker-chosen shop value, i.e., the equality the code implicitly relies on — `signed_bytes == identity_bytes` — does not hold: the bytes that are HMAC-verified (`raw_body`) are not the bytes that establish which tenant the event is attributed to (`shop` header).

### Impact Explanation
If the host application's webhook handler uses `data.shop` to key per-tenant state (e.g., look up or mutate a merchant's session, inventory, order records, or compliance data) without independently confirming the shop from the body content, an attacker can inject events attributed to an arbitrary victim shop merely by controlling the headers of a request that carries a validly-HMAC'd body they obtained from their own store's webhook traffic. This is a cross-tenant integrity/confusion issue: data or actions intended for shop A can be attributed to shop B purely based on unauthenticated header content, satisfying the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires no special privilege beyond installing the app on any shop (an ordinary/legitimate action available to any unprivileged internet user who can create a Shopify dev/partner store), and then replaying a captured request to the app's public webhook URL with a modified `shop-domain` header — no access token, `client_secret`, or TLS interception is needed. The likelihood is tempered by the amount of shop-identifying data actually present in a given topic's `body` (some payloads, such as `app/uninstalled` or GDPR topics, include shop-identifying fields the app could cross-check, while many others, e.g. generic resource `create`/`update` topics, do not).

### Recommendation
Do not trust header-derived identity fields (`shop`, `topic`, `webhook_id`) as authenticated on their own. Where possible, cross-validate the `shop` header against shop-identifying data embedded in the payload, or require the host application to only look up state using values it has independently verified are valid for the resolved shop rather than the header alone. Document clearly (or enforce in the gem) that `WebhookMetadata#shop` is not covered by `HmacValidator.validate` and must not be used as the sole tenant-binding key without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` (a shop they legitimately control) and triggers a webhook event (e.g., creates a product) so Shopify delivers a webhook to the app with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid HMAC over raw_body>`, and body `raw_body`.
2. Attacker captures `raw_body` and the valid `X-Shopify-Hmac-Sha256` value.
3. Attacker sends a new HTTP request directly to the app's public webhook endpoint with the same `raw_body` and `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body` [5](#0-4) .
5. `Registry.process` calls the app handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` [6](#0-5) , causing the app to act as if the event originated from the victim's shop.

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
