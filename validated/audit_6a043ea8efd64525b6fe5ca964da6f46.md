Based on my analysis, I found a concrete finding matching the report's bug class.

### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC signs only the raw body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only that the body's HMAC matches, then forwards `request.shop` unchecked to the app's webhook handler [3](#0-2) .

### Finding Description
The identity binding that should hold is: `shop asserted to the handler == shop that the HMAC-signed body actually originated from`. In this gem, the HMAC (`Utils::HmacValidator.validate`) only proves that the raw body bytes were signed with the app's `api_secret_key` [4](#0-3) ; it says nothing about which shop's header values accompanied that body. Because the Shopify app `client_secret`/webhook signing secret is the same for every shop that installs the app, any body+HMAC pair that was legitimately generated for shop A remains a valid signature for the exact same body when replayed with a different `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`) header claiming to be shop B. `Registry.process` never cross-checks the header-derived `shop` against anything covered by the signature; it hands `request.shop` straight to `WebhookMetadata` and the handler [5](#0-4) .

An attacker who controls a shop that has the vulnerable app installed (i.e., any merchant, since apps are installable by any unprivileged Shopify merchant) can capture a legitimate webhook body/HMAC pair sent to their own endpoint, then replay that exact body+HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop. The HMAC still validates (it only covers the body), so `Registry.process` proceeds and calls the handler with `data.shop` set to the attacker-chosen victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: an app relying on `WebhookMetadata#shop` to decide which merchant's data to look up, mutate, or delete (e.g., `app/uninstalled`, `shop/update`, `customers/redact`) can be tricked into performing that action against a shop the attacker does not control. This is a cross-tenant access primitive stemming purely from this gem's webhook verification not binding the shop identity into what is cryptographically checked.

### Likelihood Explanation
Requires only: (1) the attacker installs the app on any shop they control (unprivileged, standard merchant capability) to observe a real webhook body+HMAC, and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with forged headers — no access token, `api_secret_key`, or session is needed. Body content for many webhook topics is largely attacker-influenced or predictable (e.g., triggering `app/uninstalled`, or shop-level webhooks with static bodies), making a matching body/HMAC easy to reuse across the forged `shop-domain`.

### Recommendation
Bind the shop identity into what is verified: either include the `shop-domain` (and `topic`/`webhook_id`) headers in the HMAC-signed string, or require callers of `Registry.process` to pass the expected/registered shop and assert `request.shop` equals it before dispatching to the handler. At minimum, document and enforce that host applications must cross-check `WebhookMetadata#shop` against their own known/installed-shop list before trusting it, and consider validating `request.shop` with `Utils::ShopValidator.sanitize!` to at least confirm it is a well-formed Shopify domain (this alone would not fix cross-tenant replay, but hardens the trust boundary).

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`, triggering a webhook (e.g., `app/uninstalled`) with a static/predictable body `B`.
2. Attacker's own webhook endpoint receives `raw_body = B` and header `shopify-hmac-sha256 = HMAC(secret, B)`.
3. Attacker POSTs to the target app's webhook endpoint with `raw_body = B`, the captured `shopify-hmac-sha256`, but `shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#hmac` reads the (still-valid) HMAC header, `#to_signable_string` returns `B` unchanged [6](#0-5) ; `HmacValidator.validate` succeeds because it only recomputes the HMAC over `B` [7](#0-6) .
5. `Registry.process` calls the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)` [3](#0-2) , causing the app to act on the victim shop's record using attacker-supplied body content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
