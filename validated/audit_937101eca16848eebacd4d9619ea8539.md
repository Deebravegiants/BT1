### Title
Webhook shop identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values that are handed to the app's handler come from HTTP headers that are never included in the signed material. Because a single app's `client_secret` (and therefore the HMAC key) is shared across every shop that installs the app, any holder of one valid `(body, hmac)` pair — trivially obtainable by installing the app on an attacker-controlled shop and receiving a real webhook — can replay that exact body/HMAC pair while swapping the `x-shopify-shop-domain` header to a victim shop. The signature check still passes, and the handler receives `WebhookMetadata` claiming the payload came from the victim's shop.

### Finding Description
`Request#hmac` and `Request#to_signable_string` derive the signature check purely from the raw body: [1](#0-0) [2](#0-1) 

The `shop`, `topic`, and `webhook_id` accessors, in contrast, are read straight from unauthenticated headers: [3](#0-2) 

`HmacValidator.validate` only recomputes and compares the HMAC of `to_signable_string` (the body) against the supplied `hmac`; it never binds `shop`, `topic`, or `webhook_id` into the signed string: [4](#0-3) 

`Registry.process` performs exactly this check and then forwards the unauthenticated `request.shop` (along with `topic`/`webhook_id`) straight to the app's handler as trusted identity: [5](#0-4) 

Because a given app has one `client_secret` shared across all merchant installations, the HMAC key is identical regardless of which shop actually triggered the event. This breaks the intended identity binding `authenticated_body == body_that_generated_this_shop's_event`; the equality that should hold is `hmac(secret, body) valid ⇒ shop header trustworthy`, but in fact `hmac(secret, body) valid` only proves the body is untampered — it says nothing about which shop the header claims to be from.

### Impact Explanation
An attacker who installs the same public app on their own Shopify store receives genuine webhook deliveries with a valid `(body, hmac)` pair signed under the app's real `client_secret`. By replaying that identical body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim merchant's domain, the attacker causes `Registry.process` to accept the request as authentic and invoke the app's handler with `WebhookMetadata.shop` set to the victim shop. Any host application that uses `data.shop` from the handler to look up the victim's session/access token and act on that shop's data (a standard and encouraged pattern) will perform actions or persist data against the wrong tenant, constituting cross-tenant access/confusion — the impact category explicitly listed as Critical.

### Likelihood Explanation
Reachability requires only that the attacker be able to install the target app on any shop they control (or otherwise obtain one legitimate webhook body+HMAC pair) and send a crafted HTTP POST with a modified shop header to the app's public webhook endpoint — no access token, `client_secret`, or privileged account is needed, satisfying the "unprivileged internet user" bar.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the value that is actually verified, e.g. include `shop`, `topic`, and `webhook_id` in `Request#to_signable_string` (or otherwise require the caller to independently confirm `request.shop` against a known/expected shop for the delivery, such as by validating it against a previously stored session) before trusting it in `WebhookMetadata`. At minimum, `Registry.process` should cross-check `request.shop` against an application-level authorization state rather than treating the header as authenticated once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`; Shopify delivers a real webhook `POST` with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC_SHA256(client_secret, B)`.
2. Attacker resends an identical `POST` to the same app endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC_SHA256(client_secret, B)` and finds it equals `H` — validation passes: [6](#0-5) 
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and the host app processes/attributes data as belonging to the victim shop, even though the event actually originated from the attacker's own shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
